# Runtime Hooks

Hooks are used to respond to various events in a workflow's lifecycle. Each hook maintains a list of callback
functions which are triggered by the runtime and provided particular parameters. 

For descriptions and example usage of the available runtime hooks see the [virtool_workflow.hooks](__init__.py) package.

## The `Hook` Class

`virtool_workflow.hooks.Hook` defines the following important methods;

### `.__init__`

Create a new Hook by providing;

 1. A *name* for the hook
 2. A `List[Type]` indicating the expected positional parameter types
 3. A `Type` indicating the expected return type
 
 ```python
from virtool_workflow.hooks import Hook

on_example_event = Hook("on_example_event", [str], None)
```

The `on_example_event` hook defined above expects it's callback functions to accept a `str` as the first
parameter and return `None`.

### `.callback` or `.__call__`

The `callback()` method (equivalent to `__call__`) is a decorator method that adds the
provided `Callable` to the hook's set of callbacks. 

Here is how it would be used to register a callback for the `on_example_event` hook.

```python
@on_example_event.callback
def _callback(parameter: str):
    ...
```

Equivalently; 

```python
@on_example_event
def _callback(parameter: str):
    ...
```

The callback function `_callback` can be either a regular function or a coroutine function. It can also opt to take
no parameters if the parameters provided by the hook are not required. As such, the following will work just as well.

```python
@on_example_event
async def _callback():
    ...
```

#### The `once` and `until` Options

`.callback()` also has the optional parameters `once` and `until`. The `once` flag ensures that the provided callback
function is only invoked on the next time that the hook is triggered. In contrast the `until` option ensures that a callback
will only be invoked until the next time a different `Hook` is triggered.  

```python
@on_example_event(once=True)
def _callback():
    ...
```

In the above example, `_callback` will only be invoked once, regardless of how many times `on_example_event` is triggered.

```python
on_some_other_event = Hook(...)

@on_example_event(until=on_some_other_event)
def _callback():
    ...
```

Here `_callback` will be invoked each time the `on_example_event` hook is triggered, until the next time that 
`on_some_other_event` is triggered.


### `.trigger`

The `trigger()` method invokes a hook's callback functions with the parameters provided to it. It expects to be
passed positional parameters of the same *type* and *order* as was described when the `Hook` was created. 

Here is how the `on_example_event` hook would be triggered.

```python
async def function_where_example_event_occurs():
    # the event occurs and the required parameters are ready.
    param = ...

    results = await on_example_event.trigger(param)
```

`results` is a list containing the return values of each of the callback functions, In this case it's simply
a `List[NoneType]`


## Fixture Hooks

Fixture hooks, defined using the `virtool_workflow.hooks.WorkflowFixtureHook` class, are similar to regular 
hooks except that they inject workflow fixtures into their callback functions before invoking them. The 
`virtool_workflow.WorkflowFixtureScope` instance used to inject the fixtures is the same one which is used
for the workflow functions. This means that the fixture values (instances) will be shared between the hook
callback functions and workflow functions.

Fixture hooks can still have positional parameters in the same way regular hooks do. The difference being that 
any additional parameters will identify fixtures to be injected. Also, in the same fashion as regular hooks, 
the positional parameters can be ignored as well. 

The important thing is that callback functions must either expect none of the positional parameters or all of them.
Additionally they must declare the expected positional parameters before any "fixture parameters", and in the correct 
order.

### `.__init__`

The `.__init__` method is the same as the `Hook` class.

```python
from virtool_workflow.hooks import WorkflowFixtureHook

example_fixture_hook = WorkflowFixtureHook("example_fixture_hook", [str], str)
```

### `.callback`

The `.callback` method works the same as in the `Hook` class, but does not perform any validation of the
callbacks parameters. Since the function could take an arbitrary amount of fixture parameters it doesn't make
sense to perform the validation. 

Of course, any available fixtures can be accessed within the callback function.

```python
@example_fixtue_hook
def _callback(param: str, some_fixture: Any):
    ...
```

We can also omit the `param` positional parameter and just take fixture parameters.

```python
@example_fixtue_hook
def _callback(some_fixture: Any, some_other_fixture: Any):
    ...
```

### `.trigger`

The `.trigger` method is the most changed from the `Hook` class. It expects a `WorkflowFixtureScope` as
the first parameter, followed by the positional parameters expected by the hook. 

```python
from virtool_workflow import fixture, FixtureScope

@fixture
def some_fixture():
    return "some_value"

@fixture
def some_other_fixture():
    return "some_other_value"

with WorkflowFixtureScope() as scope:
    await example_fixture_hook.trigger(scope, "positional_parameter") 
```