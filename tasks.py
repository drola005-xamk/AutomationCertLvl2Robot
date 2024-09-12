from robocorp.tasks import task
from robocorp import browser

from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive

import shutil

@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    open_the_robot_order_website()
    orders = get_orders()
    for order in orders:
        order_number = str(order["Order number"])
        close_annoying_modal()
        fill_the_form(order)
        preview_the_robot()
        screenshot = screenshot_robot(order_number)
        submit_the_order()
        pdf_file = store_receipt_as_pdf(order_number)
        embed_screenshot_to_receipt(screenshot, pdf_file)
        click_order_another_robot_button()
    archive_receipts()
    delete_temp()

def get_orders():
    """
    Downloads the orders.csv file.
    Reads the data and populates it into a 'orders' variable.
    Returns the 'orders' variable.
    """
    http = HTTP()
    http.download(
        url="https://robotsparebinindustries.com/orders.csv", 
        target_file="output/tmp/orders.csv", 
        overwrite=True
    )

    tables = Tables()
    orders = tables.read_table_from_csv(
        "output/tmp/orders.csv", 
        columns=[
            "Order number", 
            "Head", 
            "Body", 
            "Legs", 
            "Address"
        ]
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
    """Fills the form with the order n details"""
    page = browser.page()
    page.select_option("#head", str(order["Head"]))
    page.click(f'#id-body-{str(order["Body"])}')
    page.fill("input[placeholder='Enter the part number for the legs']", str(order["Legs"]))
    page.fill("#address", order["Address"])

def preview_the_robot():
    """Clicks the preview button"""
    page = browser.page()
    page.click("button:text('Preview')")

def screenshot_robot(order_number):
    """Takes a screenshot of the robot preview"""
    page = browser.page()
    robot_preview = page.query_selector("#robot-preview-image")
    path = f'output/tmp/screenshots/{order_number}.png'

    #Wait for the images to load
    image_ready = False
    while image_ready is False:
        if page.get_by_alt_text("Head").is_visible() and page.get_by_alt_text("Body").is_visible() and page.get_by_alt_text("Legs").is_visible():
            image_ready = True

    robot_preview.screenshot(path=path)
    return path

def store_receipt_as_pdf(order_number):
    """Export receipt to a pdf file with preview image"""
    page = browser.page()
    receipt_html = page.locator("#receipt").inner_html()
    path = f'output/tmp/receipts/{order_number}.pdf'
    pdf = PDF()
    pdf.html_to_pdf(receipt_html, path)
    return path

def embed_screenshot_to_receipt(screenshot, pdf_file):
    """Embeds the screenshot to the PDF file"""
    pdf = PDF()
    pdf.add_watermark_image_to_pdf(
        image_path=screenshot, 
        source_path=pdf_file, 
        output_path=pdf_file
    )

def submit_the_order():
    """
    Clicks the Order button to submit the order.
    Works as recursive function in case of error.
    """
    page = browser.page()
    page.click("#order")

    #If order button still visible error has appeared
    if page.locator("#order").is_visible():
        submit_the_order()

def click_order_another_robot_button():
    """Clicks the 'ORDER ANOTHER ROBOT' button"""
    page = browser.page()
    page.click("#order-another")

def archive_receipts():
    """Zips the PDF receipts."""
    lib = Archive()
    lib.archive_folder_with_zip('output/tmp/receipts', 'output/receipts.zip')

def delete_temp():
    """Deletes the output/tmp folder and all its contents."""
    shutil.rmtree('output/tmp')