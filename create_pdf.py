from reportlab.pdfgen import canvas

def create_dummy_pdf(filename):
    c = canvas.Canvas(filename)
    c.drawString(100, 750, "Hello, this is a test PDF document.")
    c.drawString(100, 730, "It is used to verify the text-to-speech pipeline.")
    c.drawString(100, 710, "Here is some more text to ensure we have enough content.")
    c.save()

if __name__ == "__main__":
    create_dummy_pdf("dummy.pdf")
