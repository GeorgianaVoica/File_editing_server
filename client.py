import socket
import threading
 
# Server info
SERVER_HOST = '127.0.0.1'
SERVER_PORT = 3334
 
# Menu
def display_menu():
    print("=== Menu ===")
    print("1. View file")
    print("2. Edit file")
    print("3. Save file")
    print("4. Quit editing")
    print("5. Create file")
    print("6. Delete file")
    print("7. Exit")
 
# Server login
def login():
    # Create a TCP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_HOST, SERVER_PORT))
 
    # Request username and password from user
    username = input("Insert username: ")
 
    # Send username to server
    client_socket.sendall(f"LOGIN {username}".encode('utf-8'))
 
    # Receive file list from server
    file_list = client_socket.recv(4096).decode('utf-8')
    print(f"Available files: {file_list}")
 
    return client_socket

# View file content
def view_file(client_socket):
    filename = input("Insert file name: ")
 
    # Send view request to server
    client_socket.sendall(f"VIEW {filename}".encode('utf-8'))
 
    # Receive file content from server
    # content = client_socket.recv(4096).decode('utf-8')
    # if content is not None:
    #     print(f"Contents of {filename}: {content}\n")
    # else:
    #     print("nul")
 
# Edit file content
def edit_file(client_socket):
    filename = input("Insert file name: ")
 
    # Send edit request to server
    client_socket.sendall(f"EDIT {filename}".encode('utf-8'))
 
    # Receive file content from server
    # content = client_socket.recv(4096).decode('utf-8')
    # print(f"You have taken over editing of {filename}.")
    # print(f"Current contents of {filename}:")
    # print(content)
 
    # Receive new file content from user
    # new_content = input("Insert new file content: ")
    # client_socket.sendall(f"SAVE {filename} {new_content}".encode('utf-8'))

def save_file(client_socket):
    filename = input("Insert file name: ")
 
    # Receive new file content from user
    new_content = input("Insert new file content: ")
    client_socket.sendall(f"SAVE {filename} {new_content}".encode('utf-8'))
 
# Create file
def create_file(client_socket):
    filename = input("Insert file name: ")
 
    # Send create request to server
    client_socket.sendall(f"CREATE {filename}".encode('utf-8'))
    print(f"You have created {filename}.")
 
# Delete file
def delete_file(client_socket):
    filename = input("Insert file name: ")
 
    # Send delete request to server
    client_socket.sendall(f"DELETE {filename}".encode('utf-8'))
    print(f"You have deleted {filename}.")
 
# Quit editing file
def quit_edit(client_socket):
    filename = input("Insert file name: ")
 
    # Send quit request to server
    client_socket.sendall(f"QUIT {filename}".encode('utf-8'))
    print(f"You have quit editing of {filename}.")
 
def receive(client_socket):
    while True:
        try:
            mesaj = client_socket.recv(4096).decode('utf-8')
            print(mesaj)
        except:
            break

# Main function
def main():
    # Login to server
    client_socket = login()


    while True:
        recv_thread = threading.Thread(target=receive, args=(client_socket, ))
        recv_thread.start()

        display_menu()
        choice = input("Type your choice: ")

        if choice == "1":
            # View file content
            view_file(client_socket)
 
        elif choice == "2":
            # Edit file content
            edit_file(client_socket)
 
        elif choice == "3":
            # Save file
            save_file(client_socket)
 
        elif choice == "4":
            # Quit editing file
            quit_edit(client_socket)
 
        elif choice == "5":
            create_file(client_socket)
 
        elif choice == "6":
            delete_file(client_socket)
 
        elif choice == "7":
            # Exit client
            client_socket.sendall("EXIT".encode('utf-8'))
            client_socket.close()
            break
 
        else:
            print("Invalid option.")
 
# Run main function
if __name__ == "__main__":
    main()