from django.shortcuts import render
from django.shortcuts import redirect
from wagtail.admin import messages
from wagtail.contrib.modeladmin.views import DeleteView

class CommentDeleteView(DeleteView):
    page_title = "delete comment"
    def post(self, request, *args, **kwargs):
        try:
            self.instance.is_removed = True
            self.instance.save()
            msg = f"{ self.verbose_name }'{ self.instance }' has been deleted."
            messages.success(request, msg)
            return redirect(self.index_url)
        except Exception as e:
            return e
            
