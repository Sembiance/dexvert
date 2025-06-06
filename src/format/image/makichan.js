import {Format} from "../../Format.js";

export class makichan extends Format
{
	name           = "MAKIchan Graphic";
	website        = "http://fileformats.archiveteam.org/wiki/MAKIchan_Graphics";
	ext            = [".mag", ".max", ".mki"];
	forbidExtMatch = true;
	magic          = [/^MAKI v1-[ab] bitmap$/, "MAG v2 bitmap", "Maki-chan v2 image", /^Maki-chan v1.[ab] image/, "deark: makichan", "MAGIchan graphics :mag:", /^fmt\/1469( |$)/];
	idMeta         = ({macFileType, macFileCreator}) => macFileType==="MAG!" && ["Cute", "ImB1", "xPIC"].includes(macFileCreator);
	converters     = ["recoil2png", "wuimg", "deark[module:makichan]", "nconvert[format:mag]"];		// deark & wuimg gets some dimensions wrong but nconvert messes up the output a good bit
	verify         = ({meta}) => meta.height>1 && meta.width>1;	// deark is a little too aggressive in converting things so we check height/width and forbid ext matches
}
