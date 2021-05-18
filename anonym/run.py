# noinspection PyUnresolvedReferences
from anonym.setup import logs  # has import side effect
import inject
from tengi import App

from anonym.setup.dependencies import bind_app_dependencies
from anonym.setup.daemons import create_daemon_instances


@inject.autoparams()
def main():
    inject.configure(bind_app_dependencies)
    create_daemon_instances()

    app = inject.instance(App)
    app.run()


if __name__ == '__main__':
    main()
