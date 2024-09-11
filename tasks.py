from robocorp.tasks import task
from robocorp import browser

from RPA.HTTP import HTTP
from RPA.Tables import Tables

@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    browser.configure(
        slowmo=1000,
    )
    orders = get_orders()
    open_the_robot_order_website()
    for order in orders:
        close_annoying_modal()
        fill_the_form(order)
        submit_order()
        break
        print(order)



def get_orders():
    """
    Downloads the orders.csv file.
    Reads the data and populates it into a 'orders' variable.
    Returns the 'orders' variable.
    """
    http = HTTP()
    http.download(url="https://robotsparebinindustries.com/orders.csv", overwrite=True)

    tables = Tables()
    orders = tables.read_table_from_csv(
        "orders.csv", 
        columns=["Order number", "Head", "Body", "Legs", "Address"]
    )

    return orders

def open_the_robot_order_website():
    """Navigates to the given url"""
    browser.goto("https://robotsparebinindustries.com/#/robot-order")

def close_annoying_modal():
    """Closes the modal by selecting OK"""
    page = browser.page()
    page.click("text=OK")

def fill_the_form(order):
    page = browser.page()
    page.select_option("#head", str(order["Head"]))
    page.click(f'#id-body-{str(order["Body"])}')
    page.fill("input[placeholder='Enter the part number for the legs']", str(order["Legs"]))
    page.fill("#address", order["Address"])

def submit_order():
    #Todo: click 
    return
