
# Figures API Refernce

*NOTE: The API is in pre-production development and subject to change*

## Overview

This doc is a starting point to provide infomration on the REST APIs either defined in Figures or used by Figures.

The initial goal is to provide a reference for front end development.


## Figures REST API

These are endpoints provided by Figures

We will add a version number in the path

### Courses Index

```
/figures/api/courses-index/
```

This provides a list of abbreviated course details. Example:


```
[
	{"id":"course-v1:edX+DemoX+Demo_Course","name":"edX Demonstration Course","org":"edX","number":"DemoX"},
	{"id":"course-v1:WoodWorksU+WW101+2018","name":"Introduction to Woodworking","org":"WoodWorksU","number":"WW101"},
	{"id":"course-v1:WoodWorksU+WW102+2018","name":"Introduction to Hand Tools","org":"WoodWorksU","number":"WW102"}
]
```

Results can be filtered with query parameters. Examples:

To get a list of courses for a specific organization:

```
/figures/api/courses-index/?org=edX
```

To find all courses that contain 'Introduction':

```
/figures/api/courses-index/?display_name='Introduction'
```

Please see the [CourseOverviewFilter](https://github.com/appsembler/figures/blob/master/figures/filters.py#L15) class which defines filters available.

### Users Index

```
/figures/api/user-index/
```

This provides a list of abbreviated user data. Example:

```
[
	{"id":20,"username":"miles","fullname":"Miles Davis"},
	{"id":21,"username":"dsanborn","fullname":"David Sanborn"},
	{"id":22,"username":"natelie","fullname":"Natelie Cole"},
]
```

To get a list of active users (exclude innactive users)

```
/figures/api/user-index/?is_active=True
```

As of this time, the query is case sensitive.

More filters will be added.

Please see the [UserFilterSet](https://github.com/appsembler/figures/blob/master/figures/filters.py#L47) class which defines available filter options.

### Course Enrollments

```
/figures/api/course-enrollments/
```
The purpose of this endpoint is to provide basic course enrollment information:

* Which learners are in a given course?
* Which courses is a given learner taking?

This provides a list of abbreviated course enrollment data. Example:

_NOTE: The following structure is subject to change. However a unique learner identifier (such as the user id or username) will be included in the results, as well as the course id_

```
[
	{
		"id":14,
		"course": {
			"id":"course-v1:Appsembler+EdX101+2015_Spring",
			"display_name":"edX Demonstration Course",
			"org":"Appsembler"
		},
		"user": {
			"id":22,
			"username":"natelie",
			"fullname":"Natelie Cole"
		},
		"course_id":"course-v1:Appsembler+EdX101+2015_Spring",
		"created":"2017-02-07T17:31:11.660647Z",
		"is_active":true,
		"mode":"honor"
	},
	{
		"id":2243,
		"course":{
			"id":"course-v1:Appsembler+EdX101+2015_Spring",
			"display_name":"edX Demonstration Course",
			"org":"Appsembler"
		},
		"user":{
			"id":20,
			"username":"miles",
			"fullname":"Miles Davis"
		},
		"course_id":"course-v1:Appsembler+EdX101+2015_Spring",
		"created":"2017-08-03T15:32:19.582045Z",
		"is_active":true,
		"mode":"honor"
	}
]
```

To list the learners for a specific course, provide the course_id as a query parameter:

```
/figures/api/course-enrollments/?course_id=course-v1:Appsembler+EdX101+2015_Spring
```

To list the courses that a particular learner is taing, provide the learner id:

```
/figures/api/course-enrollments/?user_id=22
```


#### Course Daily Metrics

```
/figures/api/course-daily-metrics/
```

This provides a list of all course daily metrics. Example:

```
[
	{
		"id":1,
		"average_progress":"0.35",
		"created":"2018-05-07T18:40:29.482095Z",
		"modified":"2018-05-07T18:40:29.486932Z",
		"date_for":"2018-05-06",
		"course_id":"course-v1:Appsembler+EdX101+2015_Spring",
		"enrollment_count":25,
		"active_learners_today":5,
		"average_days_to_complete":10,
		"num_learners_completed":5
	},
	{
		"id":2,
		"average_progress":"0.35",
		"created":"2018-05-07T18:40:50.139017Z",
		"modified":"2018-05-07T18:40:50.143984Z",
		"date_for":"2018-05-07",
		"course_id":"course-v1:Appsembler+EdX101+2015_Spring",
		"enrollment_count":25,
		"active_learners_today":5,
		"average_days_to_complete":9,
		"num_learners_completed":6
	}
]
```

To get metrics for a specific day:

```
/figures/api/course-daily-metrics/?date_for=2018-05-05
```

This will return a list with one record of data for the specified date


To get metrics for a date range:

```
/figures/api/course-daily-metrics/?date_0=2018-02-02&date_1=2018-05-05
```

More filters will be added to make data retrieval easier:

* `month_for=2018-05` to retrieve all course daily metrics records for May, 2018

Please see the [CourseDailyMetricsFilter](https://github.com/appsembler/figures/blob/master/figures/filters.py#L68) class which defines filters available.

#### Site Daily Metrics

```
/figures/api/site-daily-metrics/
```

This provides a list of all site daily metrics. Example:

```
[
	{ 
		"id":1,
		"created":"2018-05-07T18:23:24.841181Z",
		"modified":"2018-05-07T18:23:24.849836Z",
		"date_for":"2018-05-05",
		"cumulative_active_user_count":50,
		"todays_active_user_count":10,
		"total_user_count":100,
		"course_count":3,
		"total_enrollment_count":75
	},
	{ 
		"id":2,
		"created":"2018-05-07T18:23:24.841181Z",
		"modified":"2018-05-07T18:23:24.849836Z",
		"date_for":"2018-05-06",
		"cumulative_active_user_count":55,
		"todays_active_user_count":15,
		"total_user_count":101,
		"course_count":3,
		"
]
```

To get metrics for a specific day:

```
/figures/api/site-daily-metrics/?date_for=2018-05-05
```

This will return a list with one record of data for the specified date.


To get metrics for a date range:

```
/figures/api/site-daily-metrics/?date_0=2018-02-02&date_1=2018-05-05
```

More filters will be added to make data retrieval easier:

* `month_for=2018-05` to retrieve all site daily metrics records for May, 2018

Please see the [SiteDailyMetricsFilter](https://github.com/appsembler/figures/blob/master/figures/filters.py#L86) class which defines filters available.


## Figures REST API endpoints used for Figures UI

There are a set REST API endpoints implemented to meet the specific needs of the Figures user interface.

These are subject to change, in particular the endpoint URLS as 

_NOTE: The trailing slash is important for these endpoints. If the trailing slash is left out, then at least some of these will redirect to the Figures UI page_

### General Site Metrics

To get the set of general site metrics:

```
/figures/api/general-site-metrics/
```

### General (Summary) Course Metrics

To get a list of all courses with general (summary) metrics for each:

```
/figures/api/courses/general/
```

### Course Details

This endpoint provides a combination of course information and learner activity

```
/figures/api/courses/detail/
```

To get the data for a specific course:

```
/figures/api/course/details/<course_id>/
```

Example:

```
/figures/api/courses/detail/course-v1:edX+DemoX+Demo_Course/
```

You can also filter on org:

```
/figures/api/courses/detail/?org=edX
```


### Overview of user data endpoints

Open edX has different roles, such as, but not limited to learner (or student), course instructor, and courses staff. Figures provides a single base endpoint, `/figures/api/users` to retrieve filterable user based data data on all users.


### General (Summary) User Data

To get a list of users with summary data:

```
/figures/api/users/general/
```

### User Details



To get details for all users:

```
/figures/api/users/detail/
```

To get details for a specific user, provide the user id:

```
/figures/users/detail/10
```

To select a set of users, add the `user_ids` query parameter followed by a list of ids:

```
/figures/api/users/detail/?user_ids=1,2,3
```

To get all the users (learner) enrolled in a course, provide the course id in the `enrolled_in_course_id` query param:

```
/fgures/api/users/detail/?enrolled_in_course_id=course-v1:edX+DemoX+Demo_Course
```


## edx-platform REST API endpoints

This section provides information about REST API endpoints available in `edx-platform`

### Courses

To get a list of all courses with details in the CourseOverview model:

```
/api/courses/v1/courses/
```

To get the details on a specific course:

```
/api/courses/v1/courses/course-v1:edX+DemoX+Demo_Course
```


### Users

#### User Account settings

The user account settings api is provided via the [openedx.core.djangoapps.user_api](https://github.com/edx/edx-platform/blob/open-release/ginkgo.master/openedx/core/djangoapps/user_api/) package.

For details, see the class documentation for [AccountViewSet](https://github.com/edx/edx-platform/blob/open-release/ginkgo.master/openedx/core/djangoapps/user_api/accounts/views.py#L27)

This returns a list of one item with the currently logged in user
```
/api/user/v1/accounts
```

To get details on a specific user:

```
/api/user/v1/accounts?username=staff
```

This call returns data of the following form:

```
[
	{
		"username":"staff",
		"bio":null,
		"requires_parental_consent":true,
		"name":"",
		"country":null,
		"is_active":true,
		"profile_image":{
			"image_url_full":"http://localhost:8000/static/images/profiles/default_500.png",
			"image_url_large":"http://localhost:8000/static/images/profiles/default_120.png",
			"image_url_medium":"http://localhost:8000/static/images/profiles/default_50.png",
			"image_url_small":"http://localhost:8000/static/images/profiles/default_30.png",
			"has_image":false
			},
		"year_of_birth":null,
		"level_of_education":null,
		"accomplishments_shared":false,
		"goals":null,
		"language_proficiencies":[],
		"gender":null,
		"account_privacy":"private",
		"mailing_address":null,
		"email":"staff@example.com",
		"date_joined":"2017-07-15T16:59:45Z"
	}
]
```
