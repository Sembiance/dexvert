import {Format} from "../../Format.js";
import {TEXT_MAGIC_STRONG} from "../../Detection.js";

export class borlandDelphiForm extends Format
{
	name           = "Delphi Borland Form";
	website        = "http://fileformats.archiveteam.org/wiki/Borland_Delphi_form";
	ext            = [".dfm"];
	forbidExtMatch = true;
	filename       = [/^tform\d+$/i];
	magic          = ["Delphi compiled form", "Borland Form", "Borland Delphi - C++ Builder Form", "Borland Delphi 3/4 Form Modul", "Lazarus Form"];
	forbiddenMagic = TEXT_MAGIC_STRONG;
	converters     = ["dfm2txt[type:bin] & dfm2txt[type:res]"];
}
