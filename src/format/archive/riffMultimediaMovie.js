import {Format} from "../../Format.js";

export class riffMultimediaMovie extends Format
{
	name        = "RIFF Multimedia Movie";
	website     = "http://fileformats.archiveteam.org/wiki/RIFF_Multimedia_Movie";
	ext         = [".mmm"];
	magic       = ["MultiMedia Movie format video", /RIFF .*multimedia movie$/];
	unsupported = true;
	notes       = "deark is working on extracting the images, I'm working on extracting the sounds/strings/text";
}
