import datetime
from haystack.indexes import *
from haystack import site
from app.models import Document

class DocumentIndex(SearchIndex):
    text = CharField(document=True, use_template=True)
    pub_date = DateTimeField(model_attr='pub_date')

    def get_queryset(self):
        return Document.objects.filter(pub_date__lte=datetime.datetime.now())


site.register(Document, DocumentIndex)