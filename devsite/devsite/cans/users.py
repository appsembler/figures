'''

TODO: Create course staff users
'''

import faker
import random

from student.models import UserProfile


class UserGenerator(object):
    '''
    usernames need to be unique
    '''

    WILL_USER_SET_EDU = 0.25

    def __init__(self, count):
        self.iterations = count
        self.counter = 0
        self.fake = faker.Faker()
        self.used_names = set()

    def username(self):
        '''
        NOTE: recursion here. To make it bulletproof, limit the iterations
        '''
        username = self.fake.user_name()
        if username in self.used_names:
            return self.username()
        else:
            self.used_names.update([username])
            return username;

    def gender(self):
        return random.choice('fm ')

    def fullname(self, gender):
        return dict(
            f=self.fake.name_female(),
            m=self.fake.name_male()
            ).get(gender, self.fake.name())

    @classmethod
    def education(cls):
        edu_choices = UserProfile.LEVEL_OF_EDUCATION_CHOICES
        if random.random() < cls.WILL_USER_SET_EDU:
            return edu_choices[random.randint(0,len(edu_choices)-1)][0]

    def create_user(self):
        gender = self.gender()
        return dict(
            username=self.fake.user_name(),
            password=self.fake.password(),
            email=self.fake.email(),
            profile=dict(
                fullname=self.fullname(gender),
                gender=gender,
                country=self.fake.country_code(),
                level_of_education=self.education(),
            )
        )

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

    def next(self):
        if self.counter < self.iterations:
            self.counter += 1
            return self.create_user()
        else:
            raise StopIteration()


def generate_user_data(count):
    return [rec for rec in UserGenerator(count)]


USER_DATA = generate_user_data(100)

FIXED_USER_DATA = [

    # students

    dict(
        username='amanda',
        password='foo',
        email='amanda@example.com',
        profile=dict(
            fullname='Amanda Smith',
            gender='f',
            country='GB',
        )
    ),
    dict(
        username='bob',
        password='foo',
        email='bob@example.com',
        profile=dict(
            fullname='Bob Smith',
            gender='m',
            country='CA',
        )
    ),
    dict(
        username='charlie',
        password='foo',
        email='charlie@example.com',
        profile=dict(
            fullname='Charlie Smith',
            gender='m',
            country='US',
        )
    ),
    dict(
        username='dawn',
        password='foo',
        email='dawn@example.com',
        profile=dict(
            fullname='Dawn Smith',
            gender='f',
            country='US',
        )
    ),

    # adminds, instructors and staff
    dict(
        username='wanda',
        password='foo',
        email='wanda@example.com',
        profile=dict(
            fullname='Wanda Smith',
            gender='f',
            country='US',
        )
    )
]
