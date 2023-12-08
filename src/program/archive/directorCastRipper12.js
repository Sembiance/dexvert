import {xu} from "xu";
import {Program} from "../../Program.js";
import {path} from "std";

export class directorCastRipper12 extends Program
{
	website   = "https://github.com/n0samu/DirectorCastRipper";
	loc       = "wine";
	bin       = "DirectorCastRipper_D12/DirectorCastRipper.exe";
	exclusive = "wine";
	args      = r => ["--files", `c:\\in${r.wineCounter}\\${path.basename(r.inFile())}`, "--output-folder", `c:\\out${r.wineCounter}`, "--include-names", "--dismiss-dialogs"];
	wineData  = ({
		timeout : xu.MINUTE*5
	});
	renameOut = false;
}
//c:\dexvert\DirectorCastRipper_D12/DirectorCastRipper.exe --files c:\in0\in.dir                                                  --output-folder c:\out0               --include-names --dismiss-dialogs
//                                  DirectorCastRipper.exe --files C:\path\to\file1.dxr C:\path\to\file2.cct C:\path\to\file3.dir --output-folder C:\path\to\somefolder --include-names --dismiss-dialogs

/* --help, -h
 --version, -v
 --files <path1> <path2> ...   Director movie or cast files to export from
 --folders <path1> <path2> ... Input folders containing Director files
 --movies <path1> <path2> ...  Director movie files to export from
 --casts <path1> <path2> ...   Director cast files to export from
 --output-folder <path>        Destination folder for exported assets
 --member-types                Member categories or types to export
    Possible values:            all | image sound flash 3d text | #bitmap #picture #sound ...
    Default:                    all
 --formats                     Preferred file formats for exported assets
    Possible values:            png bmp html rtf txt
    Default:                    png html
 --include-names               Include member & cast names in exported file names
 --decompile                   Decompile protected files with ProjectorRays
 --dismiss-dialogs             Automatically dismiss dialog boxes from the Director Player
 --text-to-images              Export image snapshots of text members
*/
