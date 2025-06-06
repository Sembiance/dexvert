import {Format} from "../../Format.js";

export class xpm extends Format
{
	name         = "X11 Pixmap";
	website      = "http://fileformats.archiveteam.org/wiki/XPM";
	ext          = [".xpm", ".pm"];
	mimeType     = "image/x-xpixmap";
	magic        = ["X PixMap bitmap", "X-Windows Pixmap Image", "X pixmap image", "image/x-xpixmap", "piped xpm sequence (xpm_pipe)", "X PixMap :xpm:", /^x-fmt\/208( |$)/];
	idMeta       = ({macFileType, macFileCreator}) => macFileType==="XPM " && macFileCreator==="GKON";
	metaProvider = ["image"];
	converters   = ["convert", "gimp", "imconv[format:xpm][matchType:magic]", "nconvert[format:xpm]", "canvas[matchType:magic]", "ffmpeg[matchType:magic][outType:png]"];
}
