import {xu} from "xu";
import {Format} from "../../Format.js";

export class anex86FDI extends Format
{
	name        = "Anex86 PC98 Floppy Image";
	website     = "http://fileformats.archiveteam.org/wiki/Anex86_PC98_floppy_image";
	ext         = [".fdi"];
	magic       = ["Anex86 PC98 floppy image"];
	priority    = this.PRIORITY.LOW;
	notes       = xu.trim`
		The DiskExplorer/editdisk program is supposed to read these, but it fails on my sample files. 
		Removing the 4k header and attempting to mount the raw image sometimes fails, likely because of a disk format unique to PC98. But it's better than nothing
		I was able to extract the files by creating a HDD image with anex86 and formatting it by following: http://www.retroprograms.com/mirrors/Protocatbert/protocat.htm
		After that I could run anex86 with dos6.2 in FDD #1 and the FDI image in FDD #2. Then hit Escape and at the DOS prompt I could COPY B:\* C:
		Then I exited anex86 and then I was able to use wine editdisk.exe to open the HDD image, ctrl-a all the files and ctrl-e extract them.
		So I could automate this and support FDI extraction. But ugh does this seem fragile and not worth it since the skip first 4k and mount trick works on some files.`;
	converters = ["dd[bs:4096][skip:1] -> uniso"];
}
