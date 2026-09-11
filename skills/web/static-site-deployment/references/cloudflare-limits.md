# Cloudflare Workers/Pages Size Limits

## Hard Limits

| Limit | Value | Affects |
|-------|-------|- |
| Per-file asset | 25 MiB | Any single file |
| Workers total | 100 MiB | All uncompressed assets |
| Pages build | 50,000 files | Build output |
| Pages bandwidth | Unlimited | Visitor requests |

## Common Large Game Types

| Type | Typical Size | Notes |
|-------|-------------|------- |
| Unity WebGL | 5-50 MB | Bundle includes .data, .wasm, .code files |
| WASM games | 1-50 MB | Pre-compiled WebAssembly bundles |
| HTML5 games | 10-100 MB | Often include video/audio assets |
| Minecraft clones | 20-50 MB | Eaglercraft, CraftOS PC, etc. |

## CI/CD Detection

```bash
# Find files over 25MB
find . -type f -size +25M

# Total uncompressed size
du -sb . | awk '{print $1/1024/1024 " MB"}'

# Compressed size for upload
tar --exclude='.git' -czf - . | wc -c | awk '{print $1/1024/1024 " MB (compressed)"}'
```

## Mitigation Strategies

1. **Remove large games** - Keep only small HTML5/JS games under 5MB
2. **External hosting** - Serve large files from R2, S3, or Netlify
3. **Content delivery** - Use a separate domain/CDN for game bundles

## Pitfall

Do not attempt manual compression - pre-built game assets (Unity bundles, WASM) are already optimized. Removing the files and serving externally is the only practical solution.
