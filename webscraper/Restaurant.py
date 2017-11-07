class Restaurant:
    def __init__(self):
        self._title = None
        self._url = None
        self._rating = None
        self._votes = None
        self._tags = None
        self._address = None
        self._hours = None

    @property
    def title(self):
        return self._title

    @property
    def url(self):
        return self._url

    @property
    def rating(self):
        return self._rating

    @property
    def votes(self):
        return self._votes

    @property
    def tags(self):
        return self._tags

    @property
    def address(self):
        return self._address

    @property
    def hours(self):
        return self._hours

    @title.setter
    def title(self, title):
        self._title = title

    @url.setter
    def url(self, url):
        self._url = url

    @rating.setter
    def rating(self, rating):
        self._rating = rating

    @votes.setter
    def votes(self, votes):
        self._votes = votes

    @tags.setter
    def tags(self, tags):
        self._tags = tags

    @address.setter
    def address(self, address):
        self._address = address

    @hours.setter
    def hours(self, hours):
        self._hours = hours

    def add_tag(self, tag):
        self._tags.append(tag)

    def add_hour_to_day(self, hour, day):
        if self._hours is None:
            self._hours = {}
        self._hours[day] = hour
