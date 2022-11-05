#include <ctype.h>
#include <errno.h>
#include <stdarg.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>

struct Archive
{
    const char *name;
    const uint8_t *contents;
    size_t size;
};

static struct Archive *loadedArchives = NULL;
static int loadedArchivesCount = 0;

static char *idbFileContents;
static char *srcdirname;
static char *outdirname;

static void fatal_error(const char *msgfmt, ...)
{
    va_list args;

    fputs("error: ", stderr);

    va_start(args, msgfmt);
    vfprintf(stderr, msgfmt, args);
    va_end(args);

    fputc('\n', stderr);

    exit(1);
}

static void nonfatal_error(const char *msgfmt, ...)
{
    va_list args;

    fputs("error: ", stderr);

    va_start(args, msgfmt);
    vfprintf(stderr, msgfmt, args);
    va_end(args);

    fputc('\n', stderr);
}

static void *read_whole_file(const char *filename, size_t *pSize)
{
    FILE *file = fopen(filename, "rb");
    uint8_t *buffer;
    size_t size;

    if (file == NULL)
        fatal_error("could not open file '%s'", filename);

    // get size
    fseek(file, 0, SEEK_END);
    size = ftell(file);

    // allocate buffer
    buffer = malloc(size + 1);

    // read file
    fseek(file, 0, SEEK_SET);
    if (fread(buffer, size, 1, file) != 1)
        fatal_error("error reading from '%s'", filename);

    // null-terminate the buffer (in case of text files)
    buffer[size] = 0;

    fclose(file);

    if (pSize != NULL)
        *pSize = size;
    return buffer;
}

static const struct Archive *load_archive(const char *name)
{
    int i;
    char *path;

    // check if it's already loaded
    for (i = 0; i < loadedArchivesCount; i++)
    {
        if (strcmp(name, loadedArchives[i].name) == 0)
            return &loadedArchives[i];
    }

    // load new archive

    path = malloc(strlen(srcdirname) + 1 + strlen(name) + 1);
    sprintf(path, "%s/%s", srcdirname, name);

    i = loadedArchivesCount;
    loadedArchivesCount++;
    loadedArchives = realloc(loadedArchives, loadedArchivesCount * sizeof(*loadedArchives));

    loadedArchives[i].name = name;
    loadedArchives[i].contents = read_whole_file(path, &loadedArchives[i].size);

    free(path);
    return &loadedArchives[i];
}

static void ensure_parent_dir(char *path)
{
    char *p;

    for (p = path; *p != 0; p++)
    {
        if (*p == '/')
        {
            *p = 0;
            if (mkdir(path, S_IRWXU) != 0 && errno != EEXIST)
                fatal_error("failed to create directory '%s': %s", path, strerror(errno));
            *p = '/';
        }
    }
}

static void write_output_file(const char *filename, const void *data, size_t size,
    int perms, int decompress)
{
    int pathlen = strlen(outdirname) + 1 + strlen(filename);
    char *path = malloc(pathlen + 3);
    FILE *file;

    if (decompress)
        sprintf(path, "%s/%s.z", outdirname, filename);
    else
        sprintf(path, "%s/%s", outdirname, filename);

    //printf("writing output file '%s'\n", path);
    ensure_parent_dir(path);

    // write the file
    file = fopen(path, "wb");
    if (file == NULL)
        nonfatal_error("failed to create file '%s'", path);
    if (fwrite(data, size, 1, file) != 1)
        nonfatal_error("error writing to '%s'", path);
    fclose(file);

    //if (decompress)
    //{
     //   char cmd[1000];

        // decompress the file
       // path[pathlen] = 0;  // remove .z suffix
       // snprintf(cmd, sizeof(cmd), "uncompress -f %s", path);
       // system(cmd);
    //}

    //if (chmod(path, perms) != 0)
    //    printf("warning: could not set permissions of '%s'\n", path);

    free(path);
}

static const void *get_file_data(const struct Archive *archive, char *filename)
{
    const uint8_t *ptr = archive->contents;
    const uint8_t *end = archive->contents + archive->size;
    int len = strlen(filename);

    // search for filename
    while (ptr < end)
    {
        int i = 0;

        for (i = 0; i < len && ptr + i < end; i++)
        {
            if (ptr[i] != filename[i])
                break;
        }
        if (i == len)
            return ptr + len;  // found file
        ptr++;
    }

    printf("warning: file '%s' was not found in archive\n", filename);
    return NULL;
}

// null terminates the current token and returns a pointer to the next token
static char *token_split(char *str)
{
    while (!isspace(*str))
    {
        if (*str == 0)
            return str;  // end of string
        str++;
    }
    *str = 0;  // terminate token
    str++;

    // skip remaining whitespace
    while (isspace(*str))
        str++;
    return str;
}

// null terminates the current line and returns a pointer to the next line
static char *line_split(char *str)
{
    while (*str != '\n')
    {
        if (*str == 0)
            return str;  // end of string
        str++;
    }
    *str = 0;  // terminate line
    return str + 1;
}

static void handle_idb_line(char *line)
{
    char *currtoken;
    char *nexttoken;
    int i = 0;

    char *filename = NULL;  // name of file to extract
    char *archivename = NULL;  // archive containing the file
    int cmpsize = -1;  // compressed size of file
    int size = -1;  // uncompressed size of file
    int perms = 0;  // file permissions
    const struct Archive *archive;
    const uint8_t *data;

    // iterate over space-separated tokens in the line
    currtoken = line;
    while (currtoken[0] != 0)
    {
        nexttoken = token_split(currtoken);

        switch (i)
        {
        case 0:  // "f" or "l" depending on whether it's a file or link
            if (strcmp(currtoken, "f") != 0)
                return;  // only process actual files, not symbolic links
            break;
        case 1:  // file permissions
            perms = strtol(currtoken, NULL, 8);
            break;
        case 4:  // file name
            filename = currtoken;
            break;
        case 6:  // archive name
            archivename = currtoken;
            break;
        default:
            if (i >= 7)  // parameters
            {
                int n;

                if (sscanf(currtoken, "cmpsize(%i)", &n) == 1)
                    cmpsize = n;
                else if (sscanf(currtoken, "size(%i)", &n) == 1)
                    size = n;
            }
            break;
        }

        currtoken = nexttoken;
        i++;
    }

    if (filename == NULL || cmpsize < 0)
        fatal_error("invalid file entry");

    // strip the suffix
    char *p = strrchr(archivename, '.');
    if (p != NULL)
        *p = 0;

    printf("extracting '%s'\n", filename);

    archive = load_archive(archivename);
    data = get_file_data(archive, filename);
    if (data == NULL)
        return;

    if (cmpsize != 0)  // compressed file
    {
        // check magic value
        if (data[0] != 0x1F || data[1] != 0x9D)
            fatal_error("invalid compression header");
        size = cmpsize;
    }

    write_output_file(filename, data, size, perms, (cmpsize != 0));
}

static void extract_all_files()
{
    char *currline;
    char *nextline;

    // iterate over lines in the IDB
    currline = idbFileContents;
    while (currline[0] != 0)
    {
        nextline = line_split(currline);

        handle_idb_line(currline);

        currline = nextline;
    }
}

static void usage(char *execname)
{
    printf("usage: %s [SRC_DIR] [IDB_NAME] [OUTPUT_DIR]\n"
           "where [SRC_DIR] is the directory containing the packages\n"
           "and [IDB_NAME] is the .idb description file\n"
           "and [OUTPUT_DIR] is a directory to place the extracted files\n",
           execname);
}

int main(int argc, char **argv)
{
    if (argc == 2 && strcmp(argv[1], "-help") == 0)
    {
        usage(argv[0]);
        return 0;
    }
    if (argc != 4)
    {
        usage(argv[0]);
        return 1;
    }

    srcdirname = argv[1];
    outdirname = argv[3];

    idbFileContents = read_whole_file(argv[2], NULL);

    extract_all_files();

    return 0;
}
