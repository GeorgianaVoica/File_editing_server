# Editarea partajata de fisiere text:
# Server-ul gestioneaza o lista de fisiere text dintr-un director gazda;
 
import socket
import threading
import os
 
# Initialize the list of files
file_list = {}
 
# Load files from /files folder
for filename in os.listdir("files"):
    file_list[filename] = {
        "content": open(f"files/{filename}", "r").read(),
        "locked_by": None
    }
 
# Auth-ed clients
authenticated_clients = []
 
# Server info
SERVER_HOST = '127.0.0.1'
SERVER_PORT = 3334
 
# Handle client requests
def handle_client(client_socket):
    client_name = ""
    while True:
        # Receive request from client
        request = client_socket.recv(1024).decode('utf-8').strip()
 
        # Check request type
        
        if request.startswith("LOGIN"):
            # Take name
            client_name = request.split(" ")[1]
 
            # Auth the client
            authenticated_clients.append(client_socket)
 
            # Send file list to client
            msg = ""
            for file in file_list:
                if file_list[file]["locked_by"] == client_socket:
                    msg += f"{file} (locked by you)\n"
                elif file_list[file]["locked_by"] is not None:
                    msg += f"{file} (locked by {file_list[file]['locked_by'].getpeername()}))\n"
                elif file_list[file]["locked_by"] is None:
                    msg += file + " (unlocked)\n"
 
            # Clientul se autentifica prin nume si primeste lista fisierelor text, precum si numele utilizatorului care are in editare fiecare fisier;
            client_socket.send(msg.encode('utf-8'))
 
            # Print login info
            print(f"Login: {client_socket.getpeername()[0]} - {client_name}")
 
        elif request.startswith("VIEW"):
            # View file content
            # Orice client autentificat poate solicita spre vizualizare continutul unui fisier,
            # caz in care sever-ul ii trimite ultima versiune de pe disc a acestuia;
            _, filename = request.split(" ")
            if filename in file_list and file_list[filename]["locked_by"] == None:
                content = file_list[filename]["content"]
                if content != "":
                    client_socket.send(content.encode('utf-8'))
                else:
                    print("fisier gol")
                    client_socket.send("-".encode('utf-8'))
            elif filename in file_list and file_list[filename]["locked_by"] is not None:
                client_socket.send(f"{filename} is being edited".encode('utf-8'))
 
        elif request.startswith("EDIT"):
            # Edit file content
 
            # Un client poate solicita preluarea in editare a unui fisier disponibil, caz in care server-ul ii livreaza continutul acestuia
            # si notifica ceilalti clienti ca fisierul respectiv este in editare de catre clientul care l-a solicitat;
 
            _, filename = request.split(" ")
 
            if filename in file_list and file_list[filename]["locked_by"] == None:
                broadcast(f"{client_name} is editing {filename}", client_socket)
                file_list[filename]["locked_by"] = client_socket
                content = file_list[filename]["content"]
                if content != "":

                    client_socket.send((f'{filename} - ' + content).encode('utf-8'))
                else:
                    print("fisier gol")
                    client_socket.send("-".encode('utf-8'))
 
        elif request.startswith("SAVE"):
            # Save file content
 
            filename = request.split(" ")[1]
            new_content = " ".join(request.split(" ")[2:])
            # Clientul poate actualiza continutul fisierului, solicitand server-ului salvarea noii versiuni,
            if filename in file_list and file_list[filename]["locked_by"] == client_socket:
                # caz in care server-ul va actualiza pe disc continutul fisierului cu ce a primit de la client
                file_list[filename]["content"] = new_content
                file_list[filename]["locked_by"] = None
 
                # si va notifica toti clientii care au in vizualizare acest fisier cu noul continut
                broadcast(f"{client_name} saved {filename}, new content of the file: {new_content}", client_socket)
                
                # Delete old file
                os.remove(f"files/{filename}")
 
                # Create new file
                f = open(f"files/{filename}", "w")
                f.write(str(new_content))
                f.close()
 
        elif request.startswith("QUIT"):
            # Quit editing file
            # Clientul poate renunta la editarea fisierului, caz in care server-ul va notifica tuturor clientilor autentificati ca resursa respectiva nu mai este in editare de catre clientul care o preluase, fiind disponibila pentru preluarea in editare;
            _, filename = request.split(" ")
            if filename in file_list and file_list[filename]["locked_by"] == client_socket:
                file_list[filename]["locked_by"] = None
                broadcast(f"{client_name} quit editing {filename}", client_socket)
 
        elif request.startswith("CREATE"):
            _, filename = request.split(" ")
            if filename not in file_list:
                # Create file on disk
                f = open(f"files/{filename}", "w")
                f.close()
 
                # Add file to file list
                file_list[filename] = {
                    "content": "",
                    "locked_by": None
                }
 
                # Broadcast create
                broadcast(f"{client_name} created {filename}", client_socket)
 
        elif request.startswith("DELETE"):
            _, filename = request.split(" ")
            if filename in file_list and file_list[filename]["locked_by"] == None:
                # Delete file from disk
                os.remove(f"files/{filename}")
 
                # Delete file from file list
                del file_list[filename]
 
                # Broadcast delete
                broadcast(f"{client_name} deleted {filename}", client_socket)
 
        elif request == "EXIT":
            # Exit client
            authenticated_clients.remove(client_socket)
            client_socket.close()
            break
 
# Broadcast a message to all authenticated clients
def broadcast(message, curent_client_socket):
    for client_socket in authenticated_clients:
        if client_socket != curent_client_socket:
            client_socket.sendall(message.encode('utf-8'))
 
# Main function
def main():
    # Create a TCP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((SERVER_HOST, SERVER_PORT))
    server_socket.listen()
 
    print(f"Server listening on {SERVER_HOST}:{SERVER_PORT}...")
 
    while True:
        # Accept a client connection
        client_socket, client_address = server_socket.accept()
        print(f"Client connected - {client_address[0]}:{client_address[1]}.")
 
        # Create a thread for the client
        client_thread = threading.Thread(target=handle_client, args=(client_socket,))
        client_thread.start()
 
if __name__ == "__main__":
    main()