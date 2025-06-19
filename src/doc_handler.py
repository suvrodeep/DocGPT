import pymupdf
import base64

from typing import List, Dict
from pydantic import BaseModel


class PDFDocument(BaseModel):
    num_pages: int
    base64_images: List[str]
    doc_name: str
    doc_id: str
    page_wise_content: Dict[int, str]
    full_text: str


class Parser:
    def __init__(
            self,
            file_path: str = None,
            pdf_bytes: bytes = None,
            file_id: str = None,
            start_page: int = None,
            end_page: int = None
    ):

        if file_path is None and pdf_bytes is None:
            raise FileNotFoundError

        self.start_page = start_page
        self.end_page = end_page
        self.pdf_doc = PDFDocument

        if pdf_bytes is None:
            self.doc_handle = pymupdf.open(filename=file_path, filetype="pdf")
        else:
            self.doc_handle = pymupdf.open(stream=pdf_bytes, filetype="pdf")

        self.pdf_doc.num_pages = self.doc_handle.page_count
        self.pdf_doc.doc_name = self.doc_handle.name
        self.pdf_doc.doc_id = file_id
        self.pdf_doc.base64_images = self.pdf_to_base64_images()
        self.pdf_doc.page_wise_content = self.pdf_to_raw_text()
        self.pdf_doc.full_text = " ".join(list(self.pdf_doc.page_wise_content.values()))


    def pdf_to_raw_text(self) -> Dict[int, str]:
        """
        Extracts raw text from each page of the PDF document.
        Returns:
            A dictionary of the page numbers as keys and the page text as the value for each page of the PDF.
        """

        # Iterate over pages and get raw text
        page_wise_raw_text = {}
        for page in self.doc_handle.pages(start=self.start_page, stop=self.end_page):
            page_wise_raw_text[page.number] = page.get_text("text", flags=pymupdf.TEXT_INHIBIT_SPACES)

        return page_wise_raw_text

    def pdf_to_base64_images(self) -> List[str]:
        """
        Converts each page of a PDF to an image encoded in Base64.
        Returns:
            A list of Base64-encoded strings representing the images of each page of the PDF.
        """

        # Iterate over pages and convert them to images
        base64_images = []
        for page in self.doc_handle.pages(start=self.start_page, stop=self.end_page):
            pixmap = page.get_pixmap()  # Render page to image

            # Encode image in Base64
            image_bytes = pixmap.pil_tobytes(format="PNG")
            base64_image = base64.b64encode(image_bytes).decode("utf-8")
            base64_images.append(base64_image)

        return base64_images