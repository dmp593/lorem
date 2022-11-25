# Lorem: A Mock API using FastAPI and MongoDB

## REQUIREMENTS

- docker
- docker-compose

## HOW TO RUN


### Copy the .env.example to the .env (do this only once)

```bash
cp .env.example .env
```

#### NOTE

You can override the environment variables in the ```.env``` as fits you best, specially if you have conflicting ports.

### Start the project

```bash
docker compose up -d
```

### Stop the project:

```bash
docker compose down --rmi local
```

#### NOTE

The data is persistent, even after shutting down the containers.
In order to completly remove all data you need to also delete the volumes. To do that, when stopping the containers you should pass the --volumes option as well:

```bash
docker compose down --rmi local --volumes
````

After that, you can also delete the ```data/``` folder.

## HOW TO USE

### Creating a Resource

Send a POST request to ```":<app-port>/<resource>/"``` with the payload you want to save. Eg:

```json
{
    "code": 123,
    "foo": "bar",
    "dummy": "data"
}
```

Where ```<app-port>``` is the port you have set in the .env (check ```APP_PORT```).

The ```<resource>``` is the web path parameters where you want to save this resource. You can have unlimited paths, as it fits best to you.

#### NOTE: You  **can't** create define sub-resources like ```<resource>/<sub-resource>```

### Retrieving resources

Send GET request to ```":<app-port>/<resource>/"``` with the query parameters you want.

For example, if you created the resource "dogs" with the json:

```json
{
    "breed": "border collie",
    "size": "medium",
    "age": "3 years and 1 month",
    "height_in_kgs": 20
}
```

You then can query for any field.
This requests are all valid:

- GET ```:<app-port>/dogs/?breed=border collie```
- GET ```:<app-port>/dogs/?size=medium```
- GET ```:<app-port>/dogs/?height_in_kgs=30```

You can combine multiple filters:

- GET ```:<app-port>/dogs/?size=medium&height_in_kgs=30```

#### NOTES

1. If the lookup you provided matches multiple entities, an array is returned. Else, the entity itself.

2. By default, the page length is to return a maximum of 100 entities.
Here are examples on how you can send override it:

- GET ```:<app-port>/dogs/?_page_len_=200```
- GET ```:<app-port>/dogs/?breed=border collie&_page_len_=200```

### Deleting resources

To delete one or many entities in a resource, you can use the verb DELETE.
You can use query parameters in the same way you used in the GET request.

Imagine that the dog as a pedigree code which you know it's unique oh that resource. You can do:

- DELETE ```:<app-port>/dogs/?pedigree=<code>```

In the same way, you can delete a sub-set of entities in a resource. Eg: deleting all dogs of a breed:

- DELETE ```:<app-port>/dogs/?breed=border collie```

Finally, to drop all the entities on a resource, just call the DELETE without any query parameter:

- DELETE ```:<app-port>/dogs/```