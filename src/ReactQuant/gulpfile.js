var gulp = require('gulp');
var uglify = require('gulp-uglify');
var htmlreplace = require('gulp-html-replace');
var source = require('vinyl-source-stream');
var browserify = require('browserify');
var watchify = require('watchify');
var reactify = require('reactify');
var streamify = require('gulp-streamify');
var react = require('gulp-react');
var run = require('gulp-run');
var less = require('gulp-less');
var concat = require('gulp-concat');
var clean = require('gulp-clean')

var path = {
  HTML: 'index.html',
  MINIFIED_OUT: 'build.min.js',
  JS_OUT: 'build.js',
  CSS_OUT: 'css/main.css',
  DEST: 'public',
  DEST_BUILD: 'public/js',
  LESS_SRC: 'src/less/main.less',
  ENTRY_POINT: 'src/js/main.js',
  LOCALE_PATH: 'src/locales',
  WWW_PATH: '/usr/local/nginx/html'
};

gulp.task('less', function() {
  return gulp.src(path.LESS_SRC)
  .pipe(less())
  .pipe(concat(path.CSS_OUT))
  .pipe(gulp.dest(path.DEST));
});

gulp.task('copy', function(){
  gulp.src(path.HTML)
    .pipe(gulp.dest(path.DEST));
  gulp.src(path.LOCALE_PATH + '/*/*.*')
    .pipe(gulp.dest(path.DEST + '/locales'))
});

gulp.task('nginx', function(){
  gulp.src([path.WWW_PATH + '*/*.*', path.WWW_PATH + '*.*'])
      .pipe(clean({force: true}));
  gulp.src([path.DEST + '/*/*/*.*', path.DEST + '/*/*.*', path.DEST + '/*'])
      .pipe(gulp.dest(path.WWW_PATH));
});

gulp.task('nginx-watch', function(){
  gulp.watch([path.DEST + '/*/*/*.*', path.DEST + '/*/*.*', path.DEST + '/*'], ['nginx'])
})

gulp.task('dev-build', function(){
  browserify({
    entries: [path.ENTRY_POINT],
    transform: [reactify]
  })
    .bundle()
    .pipe(source(path.JS_OUT))
    .pipe(gulp.dest(path.DEST_BUILD));
});

gulp.task('watch', function() {
  gulp.watch([path.HTML, path.LOCALE_PATH + '/*/*.*', path.LOCALE_PATH + '/*'], ['copy']);

  var watcher  = watchify(browserify({
    entries: [path.ENTRY_POINT],
    transform: [reactify],
    debug: true,
    cache: {}, packageCache: {}, fullPaths: true
  }));

  return watcher.on('update', function () {
    watcher.bundle()
      .pipe(source(path.JS_OUT))
      .pipe(gulp.dest(path.DEST_BUILD))
      console.log('Updated');
  })
    .bundle()
    .pipe(source(path.JS_OUT))
    .pipe(gulp.dest(path.DEST_BUILD));
});

gulp.task('build', function(){
  browserify({
    entries: [path.ENTRY_POINT],
    transform: [reactify]
  })
    .bundle()
    .pipe(source(path.MINIFIED_OUT))
    .pipe(streamify(uglify()))
    .pipe(gulp.dest(path.DEST_BUILD));
});

gulp.task('replaceHTML', function(){
  gulp.src(path.HTML)
    .pipe(htmlreplace({
      'js': 'js/' + path.MINIFIED_OUT
    }))
    .pipe(gulp.dest(path.DEST));
});


gulp.task('production', ['less', 'replaceHTML', 'build']);

gulp.task('default', ['dev-build','watch']);
