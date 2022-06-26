# ROUTE_APP_LABELS = {"graphs"}


# class DBRouter:
#     def db_for_read(self, model, **hints):
#         if model._meta.app_label in ROUTE_APP_LABELS:
#             return "graphs"
#         return None

#     def db_for_write(self, model, **hints):
#         if model._meta.app_label in ROUTE_APP_LABELS:
#             return "graphs"
#         return None

#     def allow_migrate(self, db, app_label, model_name=None, **hints):
#         if app_label in ROUTE_APP_LABELS:
#             return db == "graphs"
#         return False
