import psycopg2


class clientsDB:
    def __init__(self, conn, curr):
        self.conn = conn
        self.curr = curr

    def find_client_id_on_client_params(self, name, surname, email):
        """
        Finds client on all parameters
        """
        self.curr.execute("""
        SELECT client_id FROM client WHERE name=%s and surname=%s and email=%s;
        """, (name, surname, email))
        cl = self.curr.fetchone()
        return cl[0] if cl else 'Client with such parameters not found'

    def create_tables(self):
        """
        Creates phone table and client table
        """
        self.curr.execute("""
        CREATE TABLE IF NOT EXISTS client(
            client_id SERIAL PRIMARY KEY,
            name VARCHAR(40),
            surname VARCHAR(40),
            email VARCHAR(100)                            
        );
        """)
        self.curr.execute("""
        CREATE TABLE IF NOT EXISTS phone(
            phone_id SERIAL PRIMARY KEY,
            number VARCHAR(40),
            clients_id INTEGER NOT NULL REFERENCES client(client_id)
        );
        """)
        self.conn.commit()
        return 'Tables "client" and "phone" were created'

    def drop_tables(self):
        """
        Deletes phone table and client table
        """
        self.curr.execute("DELETE FROM phone;")
        self.curr.execute("DELETE FROM client;")
        self.curr.execute("DROP TABLE phone;")
        self.curr.execute("DROP TABLE client;")
        self.conn.commit()
        return 'All data was deleted and tables "client" and "phone" were deleted'

    def add_client(self, cl_name, cl_surname, cl_email, cl_phones=None):
        """
        Adds a client
        """
        self.curr.execute("""
        INSERT INTO client(name, surname, email) VALUES(%s, %s, %s) returning client_id;
        """, (cl_name, cl_surname, cl_email))
        cl_id = self.curr.fetchone()[0]
        if cl_phones is not None:
            for phone_num in cl_phones:
                self.curr.execute("""
                INSERT INTO phone(number, clients_id) VALUES(%s, %s);
                """, (phone_num, cl_id))
        self.conn.commit()
        return f'Client was added with id {cl_id}'

    def find_client_id_on_phone(self, phone):
        """
        Finds client on phone
        """
        self.curr.execute("""
        SELECT name || ' ' || surname 
        FROM client 
        INNER JOIN phone on phone.clients_id = client.client_id
        WHERE number=%s;
        """, (phone,))
        res = self.curr.fetchone()
        return res[0] if res else 'Client with such phone number not found'

    def add_phone_to_existing_client(self, client_id, phone):
        """
        Adds phone to existing client (and check client in DB)
        """
        self.curr.execute("""
        SELECT client_id FROM client WHERE client_id=%s;
        """, (client_id,))
        cl_id = self.curr.fetchone()
        if cl_id is None:
            return 'Client with such id not found'
        else:
            self.curr.execute("""
            INSERT INTO phone(number, clients_id) VALUES(%s, %s);
            """, (phone, cl_id[0]))
            return f'Phone was added to client {cl_id[0]}'

    def change_client_data(self, client_id, new_name=None, new_surname=None, new_email=None):
        """
        Changes client's data
        """
        if new_name:
            self.curr.execute("""
            UPDATE client SET name=%s WHERE client_id=%s;
            """, (new_name, client_id))
            self.conn.commit()
        if new_surname:
            self.curr.execute("""
            UPDATE client SET surname=%s WHERE client_id=%s;
            """, (new_surname, client_id))
            self.conn.commit()
        if new_email:
            self.curr.execute("""
            UPDATE client SET email=%s WHERE client_id=%s;
            """, (new_email, client_id))
            self.conn.commit()
        if any([new_name, new_surname, new_email]):
            return "Client's data has been changed"
        else:
            return "Nothing to change"

    def delete_client(self, client_id):
        """
        Deletes client
        """
        self.curr.execute("""
        SELECT client_id FROM client WHERE client_id=%s;
        """, (client_id,))
        cl_id = self.curr.fetchone()[0]
        if cl_id is None:
            return 'Client with such id not found'
        else:
            self.curr.execute("""
            DELETE FROM phone WHERE clients_id=%s;
            """, (cl_id,))
            self.curr.execute("""
            DELETE FROM client WHERE client_id=%s;
            """, (cl_id,))
            return f"Client {cl_id} and his phones have been deleted"

    def delete_phone(self, client_id, phone):
        """
        Deletes phone
        """
        self.curr.execute("""
        SELECT phone_id FROM phone WHERE number=%s and clients_id=%s;
        """, (phone, client_id))
        ph_id = self.curr.fetchone()
        if ph_id:
            self.curr.execute("""
            DELETE FROM phone WHERE phone_id=%s;
            """, (ph_id,))
            return f"Phone number {phone} has been deleted in client with id {client_id}"
        else:
            return f"Phone {phone} not found"


if __name__ == '__main__':
    with psycopg2.connect(database='clients_db', user='postgres', password='postgres') as conn:
        with conn.cursor() as cur:
            db_work = clientsDB(conn, cur)
            print(db_work.create_tables())
            print(db_work.drop_tables())
            print(db_work.create_tables())
            print(db_work.add_client("Serg", "Galch", "eee@mail.ru", ['789456', '98456']))
            print("Client's id which has phone 789456 is", db_work.find_client_id_on_phone('789456'))
            print(db_work.find_client_id_on_client_params("No", "Found", "eee@mail.ru"))
            cl_id = db_work.find_client_id_on_client_params("Serg", "Galch", "eee@mail.ru")

            if cl_id != 'Client with such parameters not found':
                print(db_work.add_phone_to_existing_client(cl_id, '741147'))
                print(db_work.change_client_data(cl_id, "Sergei", "Galchin", "some@yandex.ru"))
                print(db_work.change_client_data(cl_id, "Serg", "Galch", "eee@mail.ru"))
                print(db_work.delete_phone(cl_id, '741147'))
                print(db_work.delete_phone(cl_id, '321'))
                print(db_work.delete_client(1))
    conn.close()
