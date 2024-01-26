import psycopg2

# Функция, создающая структуру БД (таблицы)
def create_db(conn):
    cur.execute("""
                DROP TABLE phones; 
                DROP TABLE clients;
                """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS clients(
        id SERIAL PRIMARY KEY, 
        first_name VARCHAR(30), 
        last_name VARCHAR(30), 
        email VARCHAR(30) NOT NULL);
        """)
    conn.commit()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS phones(
        id SERIAL PRIMARY KEY, 
        phone VARCHAR(30) NOT NULL,
        client_id INTEGER NOT NULL REFERENCES clients(id));
        """)
    conn.commit()


# Функция, позволяющая добавить нового клиента
def add_client(conn, first_name, last_name, email, phone=None):
    cur.execute("""
        INSERT INTO clients(first_name, last_name, email) 
        VALUES(%s, %s, %s) RETURNING id, first_name, last_name;
        """, (first_name, last_name, email))
    new_client = cur.fetchone()
    print(f'Added client {new_client}')
    if phone is not None:
        cur.execute("""
            INSERT INTO phones(client_id, phone) VALUES(%s, %s);
            """, (new_client[0], phone))
        conn.commit()


# Функция, позволяющая добавить телефон для существующего клиента
def add_phone(conn, client_id, phone):
    cur.execute("""
        INSERT INTO phones(client_id, phone) VALUES(%s, %s);
        """, (client_id, phone))
    print(f'Added {phone} for client {client_id}')
    conn.commit()


# Функция, позволяющая изменить данные о клиенте
def change_client(conn, client_id, first_name=None, last_name=None, email=None, phone=None):
    if first_name is not None:
        cur.execute("""
            UPDATE clients SET first_name=%s WHERE id=%s
            """, (first_name, client_id))
        print(f"Client {client_id}'s name has been changed to {first_name}")
    if last_name is not None:
        cur.execute("""
            UPDATE clients SET last_name=%s WHERE id=%s
            """, (last_name, client_id))
        print(f"Client {client_id}'s surname has been changed to {last_name}")
    if email is not None:
        cur.execute("""
            UPDATE clients SET email=%s WHERE id=%s
            """, (email, client_id))
        print(f"Client {client_id}'s e-mail address has been changed to {email}")
    if phone is not None:
        add_phone(conn, client_id, phone)
        print(f'Client {client_id} added phone number {phone}')
    conn.commit()


# Функция, позволяющая удалить телефон для существующего клиента.
def delete_phone(conn, client_id, phone):
    cur.execute("""
        DELETE FROM phones WHERE client_id=%s and phone=%s;
        """, (client_id, phone))
    conn.commit()
    print(f'Phone number {phone} client {client_id} deleted')


# Функция, позволяющая удалить существующего клиента.
def delete_client(conn, client_id):
    cur.execute("""
        DELETE FROM phones WHERE client_id=%s;
        """, (client_id,))
    cur.execute("""
        DELETE FROM clients WHERE id=%s;
        """, (client_id,))
    conn.commit()
    print(f'Client {client_id} deleted')


# Функция, позволяющая найти клиента по его данным: имени, фамилии, email или телефону
def find_client(conn, first_name=None, last_name=None, email=None, phone=None):
    if phone is not None:
        cur.execute("""
            SELECT clients.id FROM clients
            JOIN phones ON phones.client_id = clients.id
            WHERE phones.phone=%s;
            """, (phone,))
    else:
        cur.execute("""
            SELECT id FROM clients 
            WHERE first_name=%s OR last_name=%s OR email=%s;
            """, (first_name, last_name, email))
    conn.commit()
    print('Client', end=' ')
    print(*cur.fetchone())



if __name__ == '__main__':
    with psycopg2.connect(database="clients_db", user="postgres", password="password") as conn:
        with conn.cursor() as cur:
            create_db(conn)

            add_client(conn, 'Elena', 'Orlova', 'Eagle@yandex.ru', '89950004444')
            add_client(conn, 'Petr', 'Petrov', 'Petrov86@mail.ru', '89997778888')
            add_client(conn, 'Ivan', 'Ivanov', 'Ivan474@gmail.com', '89990000555')
            add_client(conn, 'Maria', 'Voykovich', 'MariVoy@gmail.com', '89953330044')
            add_client(conn, 'Stepan', 'Kozhevnikov', 'IKozh76@yandex.ru')

            add_phone(conn, 1, '89997776655')
            add_phone(conn, 3, '89998887777')
            add_phone(conn, 3, '899567676767')
            add_phone(conn, 5, '89960007778')

            change_client(conn, 1, 'Olena', None, None, '899577770099')
            change_client(conn, 2, None, None, 'Petrov96@mail.ru')
            change_client(conn, 4, None, 'Kant')

            delete_phone(conn, 1, '89997776655')
            delete_phone(conn, 3, '89998887777')

            delete_client(conn, 5)

            find_client(conn, 'Olena')
            find_client(conn, None, 'Kant')
            find_client(conn, None, None, 'Petrov96@mail.ru')
            find_client(conn, None, None, None, '89990000555')
    conn.close()