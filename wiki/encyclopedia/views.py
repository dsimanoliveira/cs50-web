from django.shortcuts import render, redirect
from django.http import Http404
from django.contrib import messages
from markdown2 import Markdown
import random

from . import util

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def entry(request, title):
    if util.get_entry(title) is None:
        raise Http404("Page Not Found")
    return render(request, "encyclopedia/entry.html", {
        "title": title,
        "content": Markdown().convert(util.get_entry(title))
    })

def search(request):
    search_query = request.GET.get("q", "")
    # Check if the query matches the name of any encyclopedia entry. If does, redirect the user to the encyclopedia page.
    if search_query.upper() in [f.upper() for f in util.list_entries()]:
        return redirect('entry', title=search_query)
    # Check if the query is a substring of any of the encyclopedias entries name
    results_list = []
    if search_query:
        for entry in util.list_entries():
            if search_query.upper() in entry.upper():
                results_list.append(entry)
    return render(request, "encyclopedia/search-results.html", {
        "results": results_list
    })

def new_page(request):
    if request.method == "POST":
        title = request.POST['title']
        if title.upper() in [f.upper() for f in util.list_entries()]:
            messages.error(request, f"Page '{title}' already exists.")
            return render(request, "encyclopedia/new-page.html")
        else:
            content = request.POST['content']
            util.save_entry(title, content)
            return redirect('entry', title=title)
    else:
        return render(request, "encyclopedia/new-page.html")

def edit_page(request, title):
    if request.method == "POST":
        util.save_entry(title, request.POST['content'])
        return redirect('entry', title=title)
    else:
        return render(request, "encyclopedia/edit-page.html", {
            "title": title,
            "content": util.get_entry(title)
        })

def random_page(request):
    random_page = util.list_entries()[random.randint(0, len(util.list_entries()) - 1)]
    return redirect('entry', title=random_page)
