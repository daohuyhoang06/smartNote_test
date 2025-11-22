# project/dbrouters.py
class SmartNoteRouter:
    route_app_labels = {"ai_content"}  # app có Vocabulary, Exercise

    def db_for_read(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            return "server"   # đọc từ server db
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            return "server"   # ghi vào server db
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label in self.route_app_labels:
            return db == "server"
        return db == "default"
