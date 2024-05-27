import {Format} from "../../Format.js";

export class makichan extends Format
{
	name           = "MAKIchan Graphic";
	website        = "http://fileformats.archiveteam.org/wiki/MAKIchan_Graphics";
	ext            = [".mag", ".max", ".mki"];
	forbidExtMatch = true;
	magic          = [/^MAKI v1-[ab] bitmap$/, "MAG v2 bitmap", "Maki-chan v2 image", /^Maki-chan v1.[ab] image/, /^fmt\/1469( |$)/];
	converters     = ["recoil2png", "deark[module:makichan]"];					// deark gets some dimensions wrong
	verify         = ({meta}) => meta.height>1 && meta.width>1;	// deark is a little too aggressive in converting things so we check height/width and forbid ext matches
}
