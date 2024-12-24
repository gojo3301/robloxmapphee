import matplotlib.pyplot as plt
from io import BytesIO
from django.http import HttpResponse
import datetime
from django.shortcuts import render

def Homepage(request):
    now = datetime.datetime.now()
    subject = "Time is {}".format(now)
    return render(request,'Home.html', {'subject':subject})

def plot_view(request):
    fig, ax = plt.subplots()
    x = [1, 2, 3, 4, 5]
    y = [1, 4, 9, 16, 25]
    ax.plot(x, y)

    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    plt.close(fig)
    buffer.seek(0)

    return HttpResponse(buffer.getvalue(), content_type='image/png')

