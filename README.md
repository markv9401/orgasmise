# orgasmise
My own approach to ORGANISING unsorted, messy media files, movies, tv shows

# status
Experimental status. Use at own risk. For now, it creates symlinks without modifying the original folder structure at all.

# usage
For now, import it via
```
import orgasmise
```
and then set your basic configuration with
```
orgasmise.tmdbsimple.API_KEY = XXXXXXXXXXXXXXXX
orgasmise.input = /home/input/folder
orgasmise.output = /home/sorted/organised/output
```
at this point you're done but you can also customise misc like
```
orgasmise.video_types = ('.mkv', '.avi', '.mp4')
orgasmise.output_movies = 'Movies'
orgasmise.output_tvshows = 'TV Shows'
orgasmise.output_unknown = 'Unknown'
```

When you're done, just run
```
orgasmise.orgasmise()
```