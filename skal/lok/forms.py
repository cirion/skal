from django import forms
from django.contrib.admin import widgets

class ContactForm(forms.Form):
	TYPE_TYPO = "Typo"
	TYPE_BUG = "Bug"
	TYPE_QUESTION = "Question"
	TYPE_COMMENT = "Comment"
	TYPE_BUSINESS = "Business"
	TYPE_OTHER = "Other"
	TYPE_REASON_CHOICES = (
		(TYPE_TYPO, "I found a typo!"),
		(TYPE_BUG, "Oh no, I found a bug!"),
		(TYPE_QUESTION, "I have a question..."),
		(TYPE_COMMENT, "I just wanted to tell you something:"),
		(TYPE_BUSINESS, "I wanted to discuss business with you..."),
	)
	type = forms.ChoiceField(choices=TYPE_REASON_CHOICES, label="Oh, hey! What did you want to talk to us about?")
	message = forms.CharField(max_length=2000, widget=forms.Textarea, label="I see! Please, continue, including as much detail as possible!")
	attachment = forms.Field(label='Interesting. Hey, did you want to attach something? If so, you can do it here.', widget=forms.FileInput, required=False)
	email = forms.CharField(required=False,max_length=100, label="Uh-huh, hmmm, yes. Thanks for letting us know. If you'd like a reply, please leave your email address here. (Replies sadly not guaranteed, but we may contact you with follow-up questions or updates regarding your issue. Your email will only be used for this query, you're not being added to any mailing list.)")

