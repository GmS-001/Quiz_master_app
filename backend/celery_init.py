from celery import Celery

def celery_init_app(app):
    # This correctly configures Celery to use the uppercase variables
    # from Flask's config by looking for the "CELERY_" prefix.
    celery = Celery(app.import_name, include=['backend.celery_worker'])
    celery.config_from_object(app.config, namespace='CELERY')

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery