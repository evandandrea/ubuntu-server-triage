"""
Task object for server triage script.

This encapsulates a launchpadlib Task object, caches some queries,
stores some other properties (eg. the team-"subscribed"-ness) as needed
by callers, and presents a bunch of derived properties. All Task property
specific handling is encapsulated here.

Copyright 2017 Canonical Ltd.
Joshua Powers <josh.powers@canonical.com>
"""
from functools import lru_cache


class Task(object):
    """Our representation of a Launchpad task."""
    LONG_URL_ROOT = 'https://pad.lv/'
    SHORTLINK_ROOT = 'LP: #'
    BUG_NUMBER_LENGTH = 7

    def __init__(self):
        # Whether the team is subscribed to the bug
        self.subscribed = None
        # Whether the last activity was by us
        self.last_activity_ours = None
        self.obj = None

    @staticmethod
    def create_from_launchpadlib_object(obj, **kwargs):
        """Create object from launchpadlib"""
        self = Task()
        self.obj = obj
        for key, value in kwargs.items():
            setattr(self, key, value)
        return self

    @property
    def url(self):
        """The user-facing URL of the task"""
        return self.LONG_URL_ROOT + self.number

    @property
    def shortlink(self):
        """The user-facing "shortlink" that gnome-terminal will autolink"""
        return self.SHORTLINK_ROOT + self.number

    @property
    @lru_cache()
    def number(self):
        """The bug number as a string"""
        # This could be str(self.obj.bug.id) but using self.title is
        # significantly faster
        return self.title.split(' ')[1].replace('#', '')

    @property
    @lru_cache()
    def src(self):
        # This could be self.target.name but using self.title is
        # significantly faster
        """The source package name"""
        return self.title.split(' ')[3]

    @property
    @lru_cache()
    def title(self):
        """The "title" as returned by launchpadlib"""
        return self.obj.title

    @property
    @lru_cache()
    def status(self):
        """The "status" as returned by launchpadlib"""
        return self.obj.status

    @property
    @lru_cache()
    def short_title(self):
        """Just the bug summary"""
        # This could be self.obj.bug.title but using self.title is
        # significantly faster
        return ' '.join(self.title.split(' ')[5:]).replace('"', '')

    def compose_pretty(self, shortlinks=True):
        """Compose a printable line of relevant information"""
        if shortlinks:
            format_string = (
                '%-' +
                str(self.BUG_NUMBER_LENGTH + len(self.SHORTLINK_ROOT)) +
                's'
            )
            bug_url = format_string % self.shortlink
        else:
            format_string = (
                '%-' +
                str(self.BUG_NUMBER_LENGTH + len(self.LONG_URL_ROOT)) +
                's'
            )
            bug_url = format_string % self.url

        flags = '%s%s' % (
            '*' if self.subscribed else '',
            '†' if self.last_activity_ours else '',
        )

        return '%s - %-16s %-16s - %s' % (
            bug_url,
            ('%s(%s)' % (flags, self.status)),
            ('[%s]' % self.src), self.short_title
        )

    def sort_key(self):
        """Sort method"""
        return (not self.last_activity_ours, self.src)
