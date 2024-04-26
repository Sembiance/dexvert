import {xu} from "xu";
import {Program} from "../../Program.js";
import {path} from "std";

const _FORMAT_KEYS =
{
	wp            : ["Left"],
	wp5           : ["Up", "Up", "Up", "Left"],
	word          : ["Up", "Up", "Up", "Up", "Up", "Left"],
	word5         : ["Up", "Up", "Up", "Up", "Left"],
	multiMate     : ["Up", "Up", "Left"],
	wordStar2000  : ["Up", "Left"],
	wangIWP       : ["Down", "Down", "Down", "Left"],
	samna         : ["Down", "Down", "Down", "Down", "Left"],
	volkswriter3  : ["Down", "Down", "Down", "Down", "Down", "Left"],
	wpsPlusDX     : ["Down", "Down", "Down", "Down", "Down", "Down", "Left"],
	wordMARC      : ["Down", "Down", "Down", "Down", "Down", "Down", "Down", "Left"],
	borlandSprint : ["Down", "Down", "Down", "Down", "Down", "Down", "Down", "Down", "Left"],
	ceoWrite      : ["Down", "Down", "Down", "Down", "Down", "Down", "Down", "Down", "Down", "Left"],
	navyDIF       : ["Down", "Down", "Down", "Down", "Down", "Down", "Down", "Down", "Down", "Down", "Left"]
};

export class softwareBridge extends Program
{
	website   = "https://winworldpc.com/product/software-bridge%20/3x";
	unsafe    = true;
	flags     = {
		format : "Specify the input file format."
	};
	loc       = "dos";
	bin       = "SB/SB.EXE";
	dosData   = r => ({
		timeout  : xu.MINUTE,
		keys : [
			{delay : xu.SECOND*3},
			"3",  {delay : 500},
			["Down", "Down", "Down", "Down", "Down", "Right"],
			_FORMAT_KEYS[r.flags.format], {delay : 500},
			["F3"], {delay : 500}, `E:\\${r.f.outDir.base}`, {delay : 500}, ["Enter"], {delay : 500}, ["Escape"], {delay : 500},
			["Escape"], {delay : 500},
			"1", {delay : 500},
			`E:\\${path.basename(r.inFile())}`, {delay : 500}, ["Enter"], {delay : 500}, ["F1"],
			{delay : xu.SECOND*5},
			["Escape"], {delay : 500}, "4"
		]
	});
	renameOut = true;
	chain     = "dexvert[asFormat:document/revisableFormText]";
}
