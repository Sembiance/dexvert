// Vibe coded by Codex

#include <adplug/adplug.h>

#include <iostream>

int main()
{
    for (const CPlayerDesc *format : CAdPlug::players) {
        for (unsigned int index = 0;; ++index) {
            const char *extension = format->get_extension(index);
            if (extension == nullptr)
                break;

            std::cout << extension << ": " << format->filetype << '\n';
        }
    }

    return 0;
}
