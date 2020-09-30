import urllib.error
import urllib.request


class Node:
    running = None
    warning_shown = False

    @classmethod
    def is_running(cls):
        if cls.running is None:
            try:
                urllib.request.urlopen("http://localhost:8080/")
                cls.running = True
            except urllib.error.URLError:
                cls.running = False
                if not cls.warning_shown:
                    cls._show_not_running_warning()

        return cls.running

    @classmethod
    def _show_not_running_warning(cls):
        cls.warning_shown = True

        red_message = "\x1b[1;31m{}\033[0m"
        green_message = "\x1b[1;32m{}\033[0m"
        print(
            red_message.format(
                "WARNING: to run Ftests with `settings.DEV_MODE = True` you need to start Node server `npm run serve`."
            )
        )
        input(
            "Start Node server now if you want Ftests to be run, otherwise they will return errors,"
            " press Enter to continue..."
        )

        # Reset running attribute in case user has run Node
        cls.running = None
        cls.is_running()

        running_status = green_message.format(cls.running) if cls.running else red_message.format(cls.running)
        print(f"\nContinue with Node.running: {running_status}")
