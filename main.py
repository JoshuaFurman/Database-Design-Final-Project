import sqlite3
import random
from sqlite3 import Error
#for random number
from random import randint
#for date variables
from datetime import datetime



# This is a class to interact with the database
class Database:
    def __init__(self):
        # Try to make a connection to the database
        try:
            self.con = sqlite3.connect('Project4.db')
        except Error:
            print(Error)

        # Creates a cursor object which is used to execute queries
        self.cursor = self.con.cursor()

    #logs user in -- checks if user & password match in database
    def login(self, user, password):
        tuple = (user,password,)
        data = self.cursor.execute('SELECT priviledge FROM login WHERE user = ? AND pass = ?', tuple)
        data = self.cursor.fetchall() # cursor.fetchall() returns all the data from the query as a list of tuples
        if len(data) == 0:
            return 'none'
        else:
            for row in data:
                return row[0]
    #checks to see res_num exists in customers

    #gets id of user logged in
    def getuserid(self, user):
        tuple = (user,)
        data = self.cursor.execute('SELECT agent_id FROM agents WHERE username = ?', tuple)
        data = self.cursor.fetchall() # cursor.fetchall() returns all the data from the query as a list of tuples
        for row in data:
            return row[0]
    def valid_res_num(self, res_num):
        tuple = (res_num,)
        data = self.cursor.execute('SELECT * FROM customers WHERE res_num = ?', tuple)
        data = self.cursor.fetchall() # cursor.fetchall() returns all the data from the query as a list of tuples
        if len(data) == 0:
            return False
        else:
            return True

    #checks to see unit_num exists in vehicles table
    def valid_unit_num(self, unit, avail ):
        tuple = (unit, avail,)
        data = self.cursor.execute('SELECT * FROM vehicles WHERE unit_num = ? AND available = ?', tuple)
        data = self.cursor.fetchall() # cursor.fetchall() returns all the data from the query as a list of tuples
        if len(data) == 0:
            return False
        else:
            return True

    #finds agent id in table and prints information
    def get_agent_info(self, aid, update=False):
        tuple = (aid,)
        data = self.cursor.execute('SELECT * FROM agents WHERE agent_id = ?', tuple)
        data = self.cursor.fetchall() # cursor.fetchall() returns all the data from the query as a list of tuples
        if len(data) == 0:
            print("Error: That agent id does not exist!")
        else:
            for row in data : self.print_agent_info(row, update)

    def createAgent(self, tuple, password):
    #creates agent in agents table, error message if agent id or username already in use
        try:
            self.cursor.execute('INSERT INTO agents(agent_id, firstname, lastname, salary, username) VALUES(?,?,?,?,?)', tuple)
            self.con.commit() # commit() saves all changes to the database
        except Error:
            print('\n\nERROR: This agent id already exists\n\n')
            return
        print('AGENT CREATED...\n')
        try:
            tup = (tuple[4],password,'agent',)
            self.cursor.execute('INSERT INTO login(user, pass, priviledge) VALUES(?,?,?)', tup)
            self.con.commit() # commit() saves all changes to the database
        except Error:
            print('\n\nERROR: Unable to create login\n\n')
            return
        print('LOGIN CREATED!')

    # Accepts a tuple of arguments to be passed to the insert statement
    # Creates a new order in the orders tables
    # Accesses Vehicle, Customer, & Agent information to display a summary of the transaction
    def create_order(self, values):
        # A tuple holding the data to be inserted is passed as the 2nd parameter for execute()
        # values is in the order (res_num, a_id, price, unit_num, date_returned, date_rented) so to access individual parameters such as
        # unit_num you would do values[3] as it is the fourth item in the tuple, at index 3

        #creates order in orders table
        try:
            self.cursor.execute('INSERT INTO orders(res_num, a_id, price, unit_num, date_returned, date_rented) VALUES(?,?,?,?,?,?)', values)
            self.con.commit() # commit() saves all changes to the database
            print('Order added!')
        except Error:
            print('\n\nERROR: This order already exists\n\n')
            return

        #update vehicle availability
        query='UPDATE vehicles SET available =  \'no\' WHERE unit_num= \'' + values[3] + '\''
        self.cursor.execute(query)
        self.con.commit() # commit() saves all changes to the database

        # wait for user to hit enter before proceeding to next screen
        input()
        clear_screen()

  #print summary of transaction
        print('ORDER SUMMARY\n')
	    # access customer info
        tuple = (values[0],)
        data = self.cursor.execute('SELECT firstname, lastname FROM customers WHERE res_num = ?', tuple)
        data = self.cursor.fetchall()
        for row in data:
            print('CUSTOMER - ' + row[0] + ' ' + row[1] )

	    # access vehicle info
        tuple = (values[3],)
        data = self.cursor.execute('SELECT color, year, make, model FROM vehicles WHERE unit_num = ?', tuple)
        data = self.cursor.fetchall()
        for row in data:
            print('VEHICLE RENTED - ' + row[0] + ' ' + str(row[1]) + ' ' + row[2] + ' ' + row[3])


    	# access order info
        data = self.cursor.execute('SELECT date_rented, date_returned, price FROM orders WHERE res_num = \'' + values[0] + '\' and unit_num= \'' + values[3] +'\' and date_rented = \'' + values[5] + '\'')
        data = self.cursor.fetchall()
        for row in data:
            print('RENTAL TERMS - Rented on ' + row[0] + ' to be returned on ' + row[1] + ' for a total of $' + str(row[2]))


	    # access agent info
        tuple = (values[1],)
        data = self.cursor.execute('SELECT firstname, lastname FROM agents WHERE agent_id = ?', tuple)
        data = self.cursor.fetchall()
        for row in data:
            print('AGENT - '+ row[0] + ' ' + row[1] )

    def return_vehicle(self, unit):
        query='UPDATE vehicles SET available = \'yes\' WHERE  unit_num= \'' + unit +'\''
        self.cursor.execute(query)
        self.con.commit() # commit() saves all changes to the database
        #print info for car
        query='SELECT color, year, make, model FROM vehicles WHERE  unit_num= \'' + unit +'\''
        self.cursor.execute(query)
        data=self.cursor.fetchall()
        for row in data :
            print(row[0] + ' ' + str(row[1])+ ' ' + row[2] + ' ' + row[3] + ' has become available\n' )


    def create_customer(self, first, last, dob, cartype, addr):
        #find next available reservation number to assign customer
        data = self.cursor.execute('SELECT MAX(res_num) FROM customers ')
        data = self.cursor.fetchone() # cursor.fetchall() returns all the data from the query as a list of tuples
        for row in data:
            if row is None:
                res= 1000 # starting reservation number - used if no customers exist in the system already
            else:
                res = row + 1 #new customer reservation number = next available reservation number
            break
        customer = (res, first, last, dob, addr, cartype)
        self.cursor.execute('INSERT INTO customers(res_num, firstname, lastname, dob, address, car_type) VALUES(?,?,?,?,?,?)',customer)
        self.con.commit()
        print('Customer added!')
        tuple = (res,)
        data = self.cursor.execute('SELECT * FROM customers WHERE res_num = ?', tuple)
        data=self.cursor.fetchall()
        [print(row) for row in data]

    # Used to print the data from a previous order
    def print_order(self, res_num):
        # Create the query string. (value to be searched must be wrapped in '' or it will think it is a column name)
        query = 'SELECT * FROM orders WHERE res_num = \'' + res_num + '\''
        self.cursor.execute(query) # run the query using execute()
        data = self.cursor.fetchall() # cursor.fetchall() returns all the data from the query as a list of tuples
        if(len(data) == 0):
            print('Sorry but we can\'t find that order.')
        else:
            print('\n')
            [print(f'Reservation Number: {row[0]}' ) for row in data]
            [print(f'Agent ID: {row[1]}' ) for row in data]
            [print(f'Updated Price: {row[2]}' ) for row in data]
            [print(f'Unit number: {row[3]}' ) for row in data]
            [print(f'Rented Date: {row[5]}' ) for row in data]
            [print(f'Updated return date: {row[4]}' ) for row in data]
            print('Thank you!')

    #print agent information neatly
    def print_agent_info(self, row, update_format=False):
        print(f'----------------------------------------')
        if(update_format == False):
            print(f'Agent id: {row[0]}')
            print(f'First Name: {row[1]}')
            print(f'Last Name: {row[2]}')
            print(f'Salary: {row[3]}')
            print(f'Username: {row[4]}')
            print(f'----------------------------------------')
        else:
            print(f'(1) Salary: {row[3]}')
            print(f'(2) Username: {row[4]}')
            print(f'----------------------------------------')


    # Print customer data out in a neat format
    def print_customer_info(self, row, update_format=False):
        if(update_format == True):
            print(f'----------------------------------------')
            print(f'(1) First Name: {row[1]}')
            print(f'(2) Last Name: {row[2]}')
            print(f'(3) Street Address: {row[4]}')
            print(f'(4) Car Type: {row[5]}')
            print(f'----------------------------------------')
        else:
            print(f'----------------------------------------')
            print(f'Reservation Number: {row[0]}')
            print(f'First Name: {row[1]}')
            print(f'Last Name: {row[2]}')
            print(f'Date of Birth: {row[3]}')
            print(f'Street Address: {row[4]}')
            print(f'Car Type: {row[5]}')
            print(f'----------------------------------------')

    # Print existing customer information
    def print_contact(self, firstname, lastname, update_format=False):
        #create a query based on first and last name
        query = 'SELECT * FROM customers WHERE firstname= \'' + firstname.capitalize() + '\' and lastname= \'' + lastname.capitalize() +'\''
        self.cursor.execute(query)
        data=self.cursor.fetchall()

        if(len(data) == 0):
            print('Sorry but we can\'t find that customer.')
            return -1
        else:
            print('\nWe have your information right here.')
            if(update_format == True):
                [self.print_customer_info(row, True) for row in data] # self.print_customer_info() prints info in a neat format
                return data[0][0]  # returns the res_num
            else:
                [self.print_customer_info(row) for row in data] # self.print_customer_info() prints info in a neat format
                return None

    def get_price(self, unit_num_,days):
        price=float
        #tax=float(0.25)
        query='SELECT car_type FROM vehicles WHERE unit_num= \'' + unit_num_ + '\''
        self.cursor.execute(query)
        data=self.cursor.fetchall()
        if(len(data) == 0):
           print('Sorry we dont have that unit number.')

        elif(data[0]== ('ICAR',)):
           # print('Based on that unit number you are selecting and intermidiate car.')
            tax= 6.0 * days * 0.25
            price= 6.0 * days +tax
            return price
        elif(data[0] ==('CCAR',)):
            tax= 10.0 * days * 0.25
            price=10.0 * days + tax
            return price
        elif(data[0] == ('FCAR',)):
            tax= 15.0 * days * 0.25
            price=15 * days + tax
            return price
        elif(data[0] == ('SCAR',)):
            tax= 18.0 * days * 0.25
            price= 18.0 * days + tax
            return price
        elif(data[0] == ('XCAR',)):
            tax= 25.0 * days * 0.25
            price =25 * days +tax
            return price

    #find specified order, update return date and new price for changed rental period
    def update_returnDate(self, res, unit, old, new):
        #check that order exists & grab the date rented for new price calculation
        query='SELECT date_rented FROM orders WHERE res_num = \'' + res + '\' and unit_num= \'' + unit +'\' and date_returned = \'' + old + '\''
        self.cursor.execute(query)
        data=self.cursor.fetchall()

        if(len(data)==0):
            print('Order could not be found\n\n')
            return
        else:
            #grab date rented for new price calculation
            for row in data :
                rented = row[0]
            #create date objects to calculate days rented for price calculations
            new2 = new
            rentDate = datetime.strptime(rented, '%m/%d/%Y').date()
            returnDate =  datetime.strptime(new2, '%m/%d/%Y').date()
            days = (returnDate - rentDate).days
            price = (self.get_price(unit,days))
            price = str(price)
            #update return date & price
            query='UPDATE orders SET date_returned = \'' + new + '\', price = \'' + price + '\' WHERE res_num = \'' + res + '\' and unit_num= \'' + unit +'\' and date_returned = \'' + old + '\''
            self.cursor.execute(query)
            self.con.commit() # commit() saves all changes to the database
            print('Return date and order updated!')
            self.print_order(res)

    def print_orders(self):
        query ='SELECT * FROM orders'
        self.cursor.execute(query)
        data=self.cursor.fetchall()
        if(len(data) ==0):
            print('No orders in the system..')
        else:
            print('\n')
            print('Res_num|Aid|Price|Unit_num|Date_rented|Date_return')
            print('--------------------------------------------------')
            [print(row) for row in data]

    def available_vehicles(self, type):
        query='SELECT * FROM vehicles WHERE car_type = \'' + type +'\' and available = \'yes\''
        self.cursor.execute(query)
        data=self.cursor.fetchall()
        if(len(data)==0):
            print('No available vehicles of that type..')
        else:
            print('List of available ' + type)
            [print(row) for row in data]

    def update_agent(self, id, salary= None, username=None):
        if(salary != None):
            data = (salary, id)
            query = 'UPDATE agents SET salary = ? WHERE agent_id = ?'
            self.cursor.execute(query, data)
            self.con.commit()
        elif(username != None):
            data = (username, id)
            query = 'UPDATE agents SET username = ? WHERE agent_id = ?'
            self.cursor.execute(query, data)
            self.con.commit()

    # specify which field you want to change
    def update_info(self, res_num, first_name=None, last_name=None, address_=None, car_=None):
        if(first_name != None):
            data = (first_name, res_num)
            query = 'UPDATE customers SET firstname = ? WHERE res_num = ?'
            self.cursor.execute(query, data)
            self.con.commit()

        elif(last_name != None):
            data = (last_name, res_num)
            query = 'UPDATE customers SET lastname = ? WHERE res_num = ?'
            self.cursor.execute(query, data)
            self.con.commit()

        elif(address_ != None):
            data = (address_, res_num)
            query = 'UPDATE customers SET address = ? WHERE res_num = ?'
            self.cursor.execute(query, data)
            self.con.commit()

        elif(car_ != None):
            data = (car_, res_num)
            query = 'UPDATE customers SET car_type = ? WHERE res_num = ?'
            self.cursor.execute(query,data)
            self.con.commit()

    def return_car_type(self, res_num_):

            query='SELECT car_type FROM customers WHERE res_num = \'' + res_num_ + '\''
            self.cursor.execute(query)
            data=self.cursor.fetchall()
            ss=" "
            ss=data[0]
            ss1=ss[0]
            self.available_vehicles(ss1)

#function to clear screen
def clear_screen():
    for i in range (1,50):
                print('\r')

#functions for input validation
def getlastname():
    return input('Customer last name: ').lower().strip().capitalize()

def getfirstname():
    return input('Customer first name: ').lower().strip().capitalize()

    #returns Date object for entries into database must use ".strftime('%m/%d/%Y')" appended to returned Date object to make it a string
def getDate(datemessage):
    while(True):
        try:
            Date = input(datemessage).strip()
            Date = datetime.strptime(Date, '%m/%d/%Y').date()

        except ValueError:
            print('ERROR: that is not a valid date')
            continue
        break
    return Date

def getUnitNum(db,str):
    unit_num = input('Which vehicle is this customer renting: ').strip()
    while not(db.valid_unit_num (unit_num, 'yes')):
        print('\nERROR: Invalid unit number\n')
        unit_num = input('Which vehicle is this customer renting: ').strip()
    return unit_num

def getResNum(db):
    res_num = input('Enter customer res_num: ').strip()
    while not(db.valid_res_num(res_num)):
        print('\nERROR: Invalid reservation number\n')
        res_num = input('Enter customer res_num: ')
    return res_num

def getCarType():
    car=''
    while not(car == 'CCAR' or car == 'SCAR' or car == 'XCAR' or car == 'FCAR'or car == 'ICAR'):
        car = input('Car type:').strip().upper()
    return car

def main():
    db = Database() # creates the database object
    clear_screen()
    priviledge = 'none'
    while priviledge == 'none':

        print('LOGIN TO RENTAL SYSTEM')
        user = input('Username: ')
        password = input('Password: ')
        priviledge = db.login(user,password)
        if priviledge == 'none':
            print('\n\n\n')
            print('INVALID USERNAME OR PASSWORD')
            input('Press enter to try again...')
            clear_screen()
    clear_screen()
    print("Logging in as " + priviledge + "...")
    clear_screen()

    print('---------------------------------------')
    print('Welcome ' + user + ' !')
    print('---------------------------------------')
    while priviledge == 'boss':
        print('ADMINISTRATIVE ACCESS')
        answer = input('What would you like to do \n1: View agent information\n2: Add new agent\n3: Update agent information\n4: Access Rental System\nx: to exit\n').strip()
        if answer == '1':
            clear_screen()
            print("VIEW AGENT INFORMATION")
            id = input('Enter agent\'s id: ' )
            db.get_agent_info(id);
        elif answer == '2':
            print("ADD NEW AGENT")
            first = getfirstname()
            last = getlastname()
            #create agent id
            id = first[0] + last[0] + str(randint(10,99))
            print("\nAgent's id is: " + id + "\n")
            salary = input('Salary: ')
            print('\n\n-------------------------------------------')
            print('Allow new agent to create login information')
            print('-------------------------------------------')
            user = input('Username: ').strip()
            password = input('Password: ').strip()
            tuple = (id, first, last, salary, user,)
            db.createAgent(tuple, password)
        elif answer == '3':
            clear_screen()
            print("UPDATE AGENT INFORMATION")
            id = input('Enter agent\'s id: ' )
            db.get_agent_info(id,True)
            choice = int(input('\nWhat would you like to update?\n').strip())
            if(choice == 1):
                new_salary = float(input('Updated salary:').strip())# clean new salary
                db.update_agent(id, salary=new_salary)
                print('\nUpdated info:\n')
                db.get_agent_info(id)
            elif(choice == 2):
                new_user = input('Updated username:').strip() # clean username
                db.update_agent(id, username=new_user)
                print('\nUpdated info:\n')
                db.get_agent_info(id)

        elif answer =='4':
            access = True
            print("\n\nSWITCHING TO RENTAL SYSTEM")
            clear_screen()
            break
        elif(answer.lower() == 'x'):
             exit(0) # kills the program, exit code 0 indicates a successful exit
        else:
             print('That was not an option. Try again.')
        # wait for user to hit enter before proceeding to next screen
        print('\nPlease press enter to continue.')
        input()
        clear_screen()

    while priviledge == 'agent' or access == True:
        print('RENTAL SYSTEM')
        answer = input('What would you like to do \n1: Access Customer Info\n2: Add New Customer \n3: View Orders\n4: Create Order \n5: Return Vehicle \n6: Change Return Date of Order \n7: Check Available vehicles \n8: Update Customer Info \nx: Exit \nSelection: ').strip()
        clear_screen()
        if(answer == '1'):
            print('CUSTOMER INFORMATION REQUEST')
            print('----------------------------')
            last_name = getlastname()
            first_name = getfirstname()
            db.print_contact(first_name, last_name)

        elif(answer == '2'):
            print('GATHER CUSTOMER INFORMATION')
            print('---------------------------')
            #gets name information & formats it
            last_name = getlastname()
            first_name = getfirstname()
            #validates birthdate
            DoB = getDate('Date of Birth in format MM/DD/YYYY: ').strftime('%m/%d/%Y')
            #to control format of address we could ask for it by parts
            #number? street? city? state? ... checking the parts & concatenating the string?
            address = input('Address: ')
            #check car type & format to all caps
            car_type = getCarType()
            db.create_customer(first_name, last_name, DoB, car_type, address)
        elif (answer == '3'):
            print('VIEW RENTAL ORDERS')
            print('-------------------')
            db.print_orders()

        elif(answer == '4'):
            print('CREATE RENTAL ORDER')
            print('-------------------')
            #validate reservation number in the system
            print('For which Customer are you making an order for?')
            res_num = getResNum(db)
            db.return_car_type(res_num)
            #validate unit number in the system
            unit_num = getUnitNum(db,'yes')

            #get & validate that dates enter are actual dates before continuing
            date_rented = getDate('Date rented in format MM/DD/YYYY: ') #Date object for days calc
            date_rent = date_rented.strftime('%m/%d/%Y')  #date as a string for database entry
            date_returned = getDate('Date to return in format MM/DD/YYYY: ') #Date object for days calc
            date_return = date_returned.strftime('%m/%d/%Y') #date as a string for database entry

            days = (date_returned - date_rented).days
            price = (db.get_price(unit_num,days))

            values=(res_num,db.getuserid(user),price,unit_num,date_return,date_rent)
            #creates order in orders table & prints the summary of the contract
            db.create_order(values)

        elif(answer == '5'):
            print('RETURN VEHICLE')
            print('--------------')
            #validate unit number in the system
            unit_num = input('Unit number for vehicle returned: ').strip()
            miles = input('New milage vehicle: ').strip()

            while not(db.valid_unit_num (unit_num,'no')):
               print('\nERROR: Invalid unit number\n')
               unit_num = input('Unit number for vehicle returned: ').strip()

            db.return_vehicle(unit_num)
            print('Mileage updated to: ' + miles)



        elif(answer == '6'):
            res = input('Change the return date of an order\nEnter reservation number:').strip()
            unit = input('Enter vehicle unit num: ').strip()
            oldDate = input('Current return date MM/DD/YYYY: ').strip()
            # get & validate date
            newDate = getDate('New return date MM/DD/YYYY: ').strftime('%m/%d/%Y')

            #dbfunction to access order, update return date, update price as days rented has changed
            db.update_returnDate(res,unit,oldDate,newDate)

        elif(answer == '7'):
            print('VEHICLE AVAILABILTY')
            print('-------------------')
            car_type = input('Car type: ').upper().strip()
            db.available_vehicles(car_type)

        elif(answer == '8'):
            print('UPDATE CUSTOMER INFO')
            print('--------------------')
            while True:
                last_name = getlastname() # First and last name are capitalized in the database class methods
                first_name = getfirstname()

                # return res_num for checking with database, returns -1 if cant be found
                res_num = db.print_contact(first_name, last_name, True)
                if(res_num == -1):
                    print('\n')
                    continue
                else:
                    break

            while True:
                choice = int(input('\nWhat would you like to update?\n').strip())
                if(choice == 1):
                    new_first_name = input('Updated first name:').strip().capitalize() # clean new first name
                    db.update_info(res_num, first_name=new_first_name)
                    print('\nUpdated info:\n')
                    db.print_contact(new_first_name, last_name, True)
                    break

                elif(choice == 2):
                    new_last_name = input('Updated last name:').strip().capitalize() # clean new last name
                    db.update_info(res_num, last_name=new_last_name)
                    print('\nUpdated info:\n')
                    db.print_contact(first_name, new_last_name, True)
                    break

                # NEED TO ADD CHECKS FOR VALIDATING DATA HERE
                elif(choice == 3):
                    new_address = input('Updated address:').strip()
                    db.update_info(res_num, address_=new_address)
                    print('\nUpdated info:\n')
                    db.print_contact(first_name, last_name, True)
                    break

                # NEED TO ADD CHECKS FOR VALIDATING DATA HERE
                elif(choice == 4):
                    new_car = getCarType().upper()
                    db.update_info(res_num, car_=new_car)
                    print('\nUpdated info:\n')
                    db.print_contact(first_name, last_name, True)
                    break

        elif(answer.lower() == 'x'):
            exit(0) # kills the program, exit code 0 indicates a successful exit
        else:
            print('That was not an option. Try again.')
        # wait for user to hit enter before proceeding to next screen
        print('\nPlease press enter to continue...')
        input()
        clear_screen()


if __name__ == "__main__":
    main()
