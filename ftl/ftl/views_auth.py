# from django.contrib.auth.views import LoginView
#
#
# class LoginViewFTL(LoginView):
#     """
#     Custom login view for setting some session variables
#     (not used anymore, replaced by signals)
#     """
#
#     def form_valid(self, form):
#         valid = super().form_valid(form)
#         org = self.request.user.org
#         self.request.session['org_id'] = org.id
#         self.request.session['org_name'] = org.name
#         return valid
