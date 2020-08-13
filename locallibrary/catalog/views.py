from django.shortcuts import render
from catalog.models import Book, BookInstance, Author, Genre
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
import datetime

from django.contrib.auth.decorators import permission_required
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse

from catalog.forms import RenewBookForm

from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import PermissionRequiredMixin

from catalog.models import Author

def index(request):
    """View function for home page of site."""
    # Generate counts of some of the main objects
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()
    # Available books (status = 'a')
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()
    # The 'all()' is implied by default.    
    num_authors = Author.objects.count()
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1
    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_visits' : num_visits,
    }
    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)

class BookListView(generic.ListView):
    model = Book
    context_object_name = 'book_list'   # your own name for the list as a template variable
    queryset = Book.objects.all() # Get 5 books containing the title war
    template_name = 'book_list.html'  # Specify your own template name/location
    paginate_by = 5
    # def get_context_data(self, **kwargs):
    #     # Call the base implementation first to get the context
    #     context = super(BookListView, self).get_context_data(**kwargs)
    #     # Create any data and add it to the context
    #     context['some_data'] = 'This is just some data'
    #     return context

class BookDetailView(generic.DetailView):
    model = Book
    template_name = 'book_detail.html' 

class AuthorListView(generic.ListView):
    model = Author
    context_object_name = 'author_list'
    queryset = Author.objects.all()
    template_name = 'author_list.html'
    paginate_by = 5

class AuthorDetailView(generic.DetailView):
    model = Author
    template_name = 'author_detail.html'


class LoanedBooksByUserListView(LoginRequiredMixin,     generic.ListView):
    """Generic class-based view listing books on loan to current user."""
    model = BookInstance
    template_name ='bookinstance_list_borrowed_user.html'
    paginate_by = 10
    # context_object_name = 'bookinstance_list'
    
    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).order_by('due_back')

class LoanedBooksListView(LoginRequiredMixin, generic.ListView):
    model = BookInstance
    template_name = 'list_borrowed.html'
    paginate_by = 10
    def get_queryset(self):
        return BookInstance.objects.all()

@permission_required('catalog.can_mark_returned')
def renew_book_librarian(request, pk):
    book_instance = get_object_or_404(BookInstance, pk=pk)
    # If this is a POST request then process the Form data
    if request.method == 'POST':
        # Create a form instance and populate it with data from the request (binding):
        form = RenewBookForm(request.POST)

        #check if the form is valid
        if form.is_valid():
             # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
             book_instance.due_back = form.cleaned_data['renewal_date']
             book_instance.save()

             return HttpResponseRedirect(reverse('all-borrowed'))
    # If this is a GET (or any other method) create the default form.
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})
    context = {
        'form': form,
        'book_instance': book_instance,
    }
    return render(request, 'book_renew_librarian.html', context)

class AuthorCreate(PermissionRequiredMixin,CreateView):
    permission_required = ('catalog.can_mark_returned', 'catalog.can_edit')
    model = Author
    fields = '__all__'
    initial = {'date_of_death': '05/01/2018'}
    template_name = 'author_form.html'

class AuthorUpdate(PermissionRequiredMixin,UpdateView):
    permission_required = ('catalog.can_mark_returned', 'catalog.can_edit')
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
    template_name = 'author_form.html'


class AuthorDelete(PermissionRequiredMixin,DeleteView):
    permission_required = ('catalog.can_mark_returned', 'catalog.can_edit')
    model = Author
    success_url = reverse_lazy('authors')
    template_name = 'author_form_delete.html'

class BookCreate(PermissionRequiredMixin,CreateView):
    permission_required = ('catalog.can_mark_returned', 'catalog.can_edit')
    model = Book
    template_name = 'book_form.html'

class BookDelete(PermissionRequiredMixin,DeleteView):
    permission_required = ('catalog.can_mark_returned', 'catalog.can_edit')
    model = Book
    template_name = 'book_form_delete.html'
    success_url = reverse_lazy('books')


class BookUpdate(PermissionRequiredMixin,UpdateView):
    permission_required = ('catalog.can_mark_returned', 'catalog.can_edit')
    model = Book
    template_name = 'book_form.html'
    fields = ['title', 'author', 'isbn']

