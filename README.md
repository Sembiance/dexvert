# dexvert - **D**ecompress **EX**tract con**VERT**
Convert **1,472** file formats (out of **2,404** known) into modern equilivants (png/svg/pdf/mp3/mp4/etc.)

See the lists of [SUPPORTED](SUPPORTED.md) & [UNSUPPORTED](UNSUPPORTED.md) file formats

Utilizes [Deno](https://deno.land/) and **364** helper programs running on **4** different operating systems under [QEMU](https://www.qemu.org/)

**THIS PROJECT IS NOT MAINTAINED**<br>
**IT WILL NOT BE UPDATED**<br>
**BUGS WILL NOT BE FIXED**<br>
**PULL REQUESTS WILL BE IGNORED**<br>

## Requirements
Linux with QEMU (qemu-system-x86_64) installed.
Intel CPU with these CPU features: aes avx avx2 mmx mmxext popcnt sse sse2 sse3 sse4_1 sse4_2 ssse3

## Install
Download the 12GB <a href="https://telparia.com/dexvert/dexvert-intel-1.0.0.tar.bz2">dexvert-intel-1.0.0.tar.bz2</a> and extract it (42GB)

## Usage
Run `dexserver.sh` to start the QEMU server. Wait for it to say: **dexserver ready!!!**

In a seperate terminal run `dexvert.sh <inputFile> <outputDir>` to convert a file.

Add `--keepGoing` flag to automatically convert any new files it extracts.

Add `--json` flag to also output JSON metadata about each file it converts.

## FAQ
**Q:** Why is it so big?<br>
**A:** It uses hundreds of programs with custom patches, custom kernel patches and also embeds other OS images to convert files. This just takes a bunch of space.

**Q:** Why does it take so long to start the server?<br>
**A:** It pre-spins up multiple sub OS instances to speed up conversion.

**Q:** What does `dexvert.sh` do?<br>
**A:** It tars up the input files, copies them to a QEMU server, runs commands on the QEMU server to convert the files, copies the converted files back to the local machine, and untars them.

**Q:** Why does it tar and copy in ALL other files in the same directory as the input file?<br>
**A:** MANY files require other files to convert. Such as .bin/.cue, archives may be multi-part files, images may require palette files, music files may require samples/instruments, etc. There is no way to know ahead of time which other files might be needed, so all files in the input file directory are also sent to the QEMU server.

**Q:** Why does it append the § character to the end of output directories?<br>
**A:** This is to ensure any output directories do not clobber an other files that may have been extracted naturally. You can change this suffix by passing the `--suffix` flag.

**Q:** How can a hint be passed that the file is from a certain operating system or is in a particular language so dexvert can better convert it?<br>
**A:** You can pass a `--oshint=osid` flag where osid is one of the following from the left column:
osid | OS or Language
---- | --------------
amiga | Amiga
atari | Atari ST
commodore | Commodore 64
dos | DOS/Windows
fmtownsjpy | FM Towns or Japanese
macintosh | Macintosh (or Apple 2)
macintoshjp | Macintosh Japanese
nextstep | NeXTSTEP
riscos | RISC OS

**Q:** Why does it hang or fail to convert?<br>
**A:** Bugs have crept in due to trying to get this to work within a virtual machine (it was designed to run on real hardware). Mostly relating to the sub QEMU OSes (QEMU within QEMU). I am no longer maintaining this project, so I won't be fixing it. You are welcome to fork it and track down the problems yourself.

**Q:** How can it be ran in 'administration' mode directly against the HD image (rather than a backing file) and then interactively test/fix things, etc.?<br>
**A:** You'll need an `admin.qcow2` file. Either create a blank one or download the 50G <a href="https://telparia.com/dexvert/admin.qcow2">admin.qcow2</a> file that has a full test suite with almost 18,000 sample test files. Then launch dexserver with the `--admin` flag. Note if you are crazy enough to run the test suite, it's sensitive to which CPU you have so an MP3 or MP4 produced on one system will be slightly different on another system. So you can ignore things that are off by just a few percent of bytes. The password for both `dexvert` and `root` on the QEMU system is `dexvert`. You may want to Ctrl-C on server startup during the 10 second pause before the internal dexserver starts up.

**Q:**: Why only intel?<br>
**A:**: Wasn't able to iron out all the emulated bugs when hosting it on an AMD system. If you want to try it on AMD, run in admin mode (see previous question) and then switch to root `emerge -1 -e @world` that will recompile all packages for the current CPU, which would be your AMD (as QEMU was ran with -cpu host). Good luck.

**Q:**: I have another question<br>
**A:**: You can contact me with questions, but note that I've abandonded this project so while I can answer some questions I won't be doing any code changes or bug fixes or anything else.
