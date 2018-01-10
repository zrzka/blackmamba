# Contribution

There are several areas where you can help.

## Documentation

I'm not native English speaker and some of my sentences sound weird.
Fork [blackmamba](https://github.com/zrzka/blackmamba) repository,
update [documentation](https://github.com/zrzka/blackmamba/tree/master/docs/source) and
open pull request. Will happily merge it.

## Testing

If you find a bug, please do not hesitate to [file an issue](https://github.com/zrzka/blackmamba/issues).
I'm unable to test everything.

## Questions

Do you have a question? [File an issue](https://github.com/zrzka/blackmamba/issues), I'll add
`question` tag and will answer it. Or you can send me direct message on
[Twitter](https://twitter.com/robertvojta).

## New ideas

I'm open to new ideas as well. Please, [file an issue](https://github.com/zrzka/blackmamba/issues).


## Development

### Style

Look around and try to keep same style. There're no hard rules. Just one and it's about
documentation strings. [Google Style](http://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html)
is used with minimum amount of reStructuredText features. That's because the documentation
string must be readable even in the console as a plain string.  


### Pull requests

Pull requests must pass `flake8` checks:

```
flake8 . --count --select=E901,E999,F821,F822,F823 --show-source --statistics
flake8 . --count --max-complexity=10 --max-line-length=127 --statistics
```

Pull requests must pass tests:

```
PYTHONPATH=. pytest tests
```

Consult [.travis.yml](https://github.com/zrzka/blackmamba/blob/master/.travis.yml) for more details.
