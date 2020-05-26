### front-end deploy:  
- an updated version with sample query: [https://dj91iptgrvxcf.cloudfront.net](https://dj91iptgrvxcf.cloudfront.net)
- [https://dlvahlk17v2d8.cloudfront.net](https://dlvahlk17v2d8.cloudfront.net)
- s3 endpoint (need https traffic to use speech recognition): [http://photo-album-app-test.s3-website-us-east-1.amazonaws.com](http://photo-album-app-test.s3-website-us-east-1.amazonaws.com)

### structure
#### frontend
- Bucket: `photo-album-app-test`
- files:
    - js: mainly contains .js for api and speech recognitions
    - index.html: main page
    - upload.html: upload files

#### lambda
-  `photoAlbumAPP-LF1`
-  `photoAlbumAPP-LF2`

#### Lex 
- Name:  `PhotoAlbumSearch`
- Lex export configuration: PhotoAlbumSearch_Export.json
- Lex setup (with nltk): other_funcs/nltk_setup.py
