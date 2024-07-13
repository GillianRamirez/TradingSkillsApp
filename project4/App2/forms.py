from django import forms
from django.core.validators import EmailValidator
from django.forms import ModelForm
from .models import Post

# contact page
class ContactForm(forms.Form):
    name = forms.CharField(max_length=100)
    email = forms.CharField(validators=[EmailValidator()])
    phone = forms.CharField(max_length=15)
    subject = forms.CharField(max_length=100)
    message = forms.CharField(widget=forms.Textarea)

#stock view/selection

SHARE_Company_Names = (
    ('AAPL', "Apple"),
    ('GOOG', "Google"),
    ('MSFT', "Microsoft"),
)

class ShareForm(forms.Form):
    company = forms.ChoiceField(choices=SHARE_Company_Names,
                                widget=forms.Select(attrs={'onchange': 'tickerform.submit();'}))


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ["title", "description", "content"]

#portfolio

class PortfolioForm(forms.Form):
    stock_id = forms.CharField(max_length=100)
