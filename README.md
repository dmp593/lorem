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

#### NOTE

You can pass an array of entities as well; it will insert many at once (bulk write).

```POST localhost:<app-port>/canis-familiaris/``` with the payload you want to save. Eg:

```json
[
    {
        "breed": "Australian Shepherd",
        "lifespan": "13 to 15 years",
        "personality": "awesome"
    },
    {
        "breed": "Bernese Mountain Dog",
        "lifespan": "12 to 14 years",
        "personality": "fullstack family devoted"
    },
    {
        "breed": "Belgian Shepherd",
        "lifespan": "12 to 15 years",
        "personality": "olympic champ"
    },
    {
        "breed": "Border Collie",
        "lifespan": "12 to 14 years",
        "personality": "sheep it"
    },
    {
        "breed": "Dachshund",
        "lifespan": "12 to 15 years",
        "personality": "cunning hot"
    },
    {
        "breed": "Siberian Husky",
        "lifespan": "up to 12 years",
        "personality": "are you my santa?"
    }
]
```

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

The API implements smart find by id. In other words, tries to find by id if your entity has at least on of these (guessed) fields:

- ```id```
- ```uuid```
- ```code```
- ```pk```
- ```username```
- ```email```

In this case, if your entity has one of these fields, you can retrieve by id has a path parameter, instead of a query parameter.

Consider the following scenario:

```json
{
    "pk": 1,
    "breed": "german shepherd"
}
```

Then, you can do:

```GET localhost:<app-port>/dogs/{pk}```

Which is roughly equivelent to:

```GET localhost:<app-port>/dogs/?pk=1```

You may use this for convinience, but keep in mind that the second approach is more efficient, since the first approach will apply an OR clause: it tries to find the *first* entity that has that value, on each possible field name.

#### IMPORTANT

The MockAPI doesn't stop you for having duplicated entries for same "smart" ids. You must ensure the uniqueness of your data.

If you have duplicated entries, with the first approach (smart find by id) it will retrieve the *first* found. If you want to retrieve all duplicated information, please use the second approach, it will return an array of entities with the same id.

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

- ```DELETE localhost:<app-port>/dogs/?pedigree=<pedigree>```

If your entity has a field name that is considered a smart id, alternatively you can do:

- ```DELETE localhost:<app-port>/dogs/<code>/```

In the same way, you can delete a sub-set of entities in a resource. Eg: deleting all dogs of a breed:

- ```DELETE localhost:<app-port>/dogs/?breed=border collie```

Finally, to drop all the entities on a resource, just call the DELETE without any query parameter:

- ```DELETE localhost:<app-port>/dogs/```

#### IMPORTANT

The MockAPI doesn't stop you for having duplicated entries for same "smart" ids. You must ensure the uniqueness of your data.

If you have duplicated entries, with the second approach of DELETE, it will delete the *first* found with that "smart" id. If you want to delete all duplicated information for the same "smart" id, please use the first approach.

### Advanced Query Parameters

For advanced usage on query parameters, you can specify the operator by separating it from the field name with double underscore.
Usage: \<key\>_\_\<operator\>=\<value\>

For example, get all the dogs with the id greater then 100: ```GET localhost:<app-port>/dogs/?id__gt=100```

Operators available:

- ```eq``` (equals)
- ```ne``` (not equals)
- ```neq``` (not equals [alias of ```ne```])
- ```startswith``` (string starts with)
- ```istartswith``` (string starts with [case insensitive])
- ```contains``` (contains string)
- ```icontains``` (contains string [case insensitive])
- ```endswith``` (string ends with)
- ```iendswith``` (string ends with [case insensitive])
- ```exists``` (the value exists/is present in the entity)
- ```nexists``` (the value not exists/is present in the entity)
- ```notexists``` (the value not exists/is present in the entity [alias of ```nexists```])
- ```null``` (the value exists and is null)
- ```isnull``` (the value exists and is null [alias of ```null```])
- ```notnull``` (the value exists and is not null)
- ```isnotnull``` (the value exists and is not null [alias of ```notnull```])
- ```gt``` (greater then)
- ```gte``` (greater then or equal)
- ```lt``` (less then)
- ```lte``` (less then or equal)
- ```in``` (value(s) in array)
- ```nin``` (value(s) not in array)
- ```notin``` (value(s) not in array [alias of ```nin```])


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
    "canidae": {
        "caninae": {
            "canini": [
                {
                    "name": "Zeus",
                    "breed": "Rottweiler"
                },
                {
                    "name": "Hercules",
                    "breed": "Saint Bernard"
                },
                {
                    "name": "Ares",
                    "breed": "Pit Bull"
                }
            ]
        }
    }
}
```

To get the all the strucutre where you know that there is one dog called Hercules as the second element, you can do:
```GET localhost:<app-port>/animals/?canidae.caninae.canini.1.name=hercules```

#### NOTE

For operators ```exists``` and ```isnull``` the truthful values are: true, TRUE, True, yes, YES, Yes, y and 1.
Everything other than these values are considered false.

Thus, in order to test the inexistence of a field or a field that must be not null, just do something like:
```GET localhost:<app-port>/dogs/?owner__isnull=0``` Gets all the dogs that have an owner :smiley:


### NOTE 2

All values in query parameters that can be parsed to numeric values, will be treated like so when possible (excluding regexes: ```\[i\]contains```, ```\[i\]startswith```, ```\[i\]endswith``` ). The app will guess the query by applying an internally an Or operator: \<expression\> OR \<numeric-expression\>.
Eq: ```foo=123``` will apply ( foo EQ '123' OR foo EQ 123 ) but ```foo=bar``` will do only ( foo EQ 'bar' ).


If the value is an array, the same rule applies Eg: ```colors__in=brown,gold,255``` will parse as ```['brown', 'gold', 255]``` and thus an OR operator will be applied.

### NOTE 3

If you pass a value separated by commas using equal/not equal operator, it will try an IN operator and also an Or operator following the NOTE 2. Eg: ```colors=brown,255``` will query: ( colors EQ 'brown,255' OR colors IN ['brown', '255'] OR colors IN ['brown', 255] ).

#### TODO/Current Limitations

1. You  **can't** create sub-resources, for example: ```localhost:<app-port>/canidae/caninae/canini/canina``` it's not allowed.
Only the root resource is allowed (```canidae```). The second resource will be treated as id. The rest of the paths don't make any sense for the MockAPI. It will not work.
2. Do not send fields starting with a dot, double underscore. The only fields allowed to start with double underscore are ```__limit``` and ```__offet``` for pagination.
3. TODO probably in the future, I will implement the __raw suffix (still thinking possibilities for this).
You can indicate the app to ignore NOTE 2 and 3 rules with this suffix.

Eg:

- ```model__raw=2394701``` will be treated \"as-is\": ( model EQ '2394701' )
- ```colors__raw=brown,gold``` will not apply NOTE 3: ( colors EQ 'brown,gold' )
- ```colors__in__raw=brown,255``` will not apply NOTE 3: ( COLORS IN ['brown', '255'] )

__raw will be an indicator to any operator to not "smart guess" the value using complex queries.

#### REMEMBER

Keep in mind that these notes and limitations can impact your queries performances and results.
