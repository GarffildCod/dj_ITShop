from django.shortcuts import render
from django.template.loader import get_template
from django.core.mail import EmailMultiAlternatives
from it_website.forms import *





def index(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

def services(request):
    return render(request, 'services.html')

def blog(request):
    return render(request, 'blog.html')

def contact(request):
    context = {}
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            send_massage(form.cleaned_data['name'], form.cleaned_data['email'], form.cleaned_data['massage'])
            context= {'succes': 1}
    else:
        form = ContactForm()
    context['form'] = form
    return render(request, 'contact.html', context=context)

def send_massage(name,email,massage):
    text = get_template('massage.html')
    html = get_template('massage.html')
    context = {'name': name, 'email': email, 'massage': massage}
    suject = 'Сообщение от пользователя'
    from_email = 'frpm@example.com'
    text_content = text.render(context)
    html_content = html.render(context)


    msg = EmailMultiAlternatives(suject, text_content, from_email, ['toyserviss@rambler.ru'])
    msg.attach_alternative(html_content, 'text/html')
    msg.send()

def shop(request):
    return render(request, 'shop.html')