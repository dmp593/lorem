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

Send the request ```POST localhost:<app-port>/<resource>/``` with the payload you want to save. Eg:

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

Send the request ```GET localhost:<app-port>/<resource>/``` with the query parameters you want.

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

- ```GET localhost:<app-port>/dogs/?breed=border collie```
- ```GET localhost:<app-port>/dogs/?size=medium```
- ```GET localhost:<app-port>/dogs/?height_in_kgs=30```

You can combine multiple filters:

- ```GET localhost:<app-port>/dogs/?size=medium&height_in_kgs=30```

#### NOTES

1. If the lookup you provided matches multiple entities, an array is returned. Else, the entity itself.

2. By default, the page length is to return a maximum of 100 entities.
Here are examples on how you can send override it:

- ```GET localhost:<app-port>/dogs/?__limit=200```
- ```GET localhost:<app-port>/dogs/?breed=border collie&__limit=200```

You can apply the offet too:

- ```GET localhost:<app-port>/dogs/?__limit=200&__offet=100```

### Deleting resources

To delete one or many entities in a resource, you can use the verb DELETE.
You can use query parameters in the same way you used in the GET request.

Imagine that the dog as a pedigree code which you know it's unique oh that resource. You can do:

- ```DELETE localhost:<app-port>/dogs/?pedigree=<code>```

In the same way, you can delete a sub-set of entities in a resource. Eg: deleting all dogs of a breed:

- ```DELETE localhost:<app-port>/dogs/?breed=border collie```

Finally, to drop all the entities on a resource, just call the DELETE without any query parameter:

- ```DELETE localhost:<app-port>/dogs/```

### Advanced Query Parameters

For advanced usage on query parameters, you can specify the operand by separating it from the field name with double underscore.
Usage: \<key\>_\_\<operand\>=\<value\>

For example, get all the users greater id 100: ```GET localhost:<app-port>/users/?id__gt=100```

Operands available:

- ```eq``` (equals)
- ```ne``` (not equals)
- ```exists``` (the value exists/is present in the entity)
- ```isnull``` (the value exists and is null)
- ```gt``` (greater then)
- ```gte``` (greater then or equal)
- ```lt``` (less then)
- ```lte``` (less then or equal)
- ```in``` (value(s) in array)
- ```nin``` (value(s) not in array)

#### Querying nested objects or arrays

If you have an object like:

```json
{
    "foo": {
        "bar": "foobar"
    }
}
```

You can query the nested object with the dot notation:

```GET localhost:<app-port>/dummies/foo.bar=foobar```

There is no limitation on nested queries with the dot notation. You can go further: foo.bar.baz=qux

Arrays are treated as objects. An index is just the field name.
Thus, having the structure:

```json
{
    "foo": {
        "bar": {
            "users": [
                {
                    "name": "dummy",
                    "address": "somewhere in the planet",
                    ...
                },
                {
                    "name": "smart",
                    "address": "around the moon",
                    ...
                }
            ]
        }
    }
}
```

To get the data of the second user, do:
```GET localhost:<app-port>/dummies/foo.bar.users.1.name=smart```

#### NOTE

For operands ```exists``` and ```isnull``` the truthful values are: true, TRUE, True, yes, YES, Yes, y and 1.
Everything other than these values are considered false.

Thus, in order to test the inexistence of a field or a field that must be not null, just do something like:
```GET localhost:<app-port>/dogs/?owner__isnull=0``` Gets all the dogs that have an owner :smiley:

#### TODO/Current Limitations

1. All values in query parameters that can be parsed to numerical values, will be treated like so. There is no escape mechanism for now.

2. If you pass a value separated by commas, it will be treated as an array. Eg: ```colors=blue,green``` will parse as ```['blue', 'green']```.
For each element in the array, the rule limitation 1 still applies. Eg: ```colors=blue,green,255``` will parse as ```['blue', 'green', 255]```.

3. Do not send fields starting with a dot, double underscore or a dollar sign.
The only fields allowed to start with double underscore are ```__limit``` and ```__offet```.

4. For now, regarding pagination, when returning a collection, there is no metadata that tells you the count until now and total count of entities in the database.

Keep in mind that these query limitations can impact your results.
