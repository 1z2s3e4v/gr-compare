#include "global.h"
#include "obj/Design.h"
#include "gr/GlobalRouter.h"

int main(int argc, char* argv[]) {
    logeol(2);
    log() << "GLOBAL ROUTER CUGR" << std::endl;
    logeol(2);
    // Parse parameters
    Parameters parameters(argc, argv);
    
    // Read LEF/DEF
    Design design(parameters);
    
    // Global router
    GlobalRouter globalRouter(design, parameters);

    /// Only transfer lefdef format to capnet (ISPD24) format
    if(parameters.transFormatToISPD24){
        log() << "Start transfering lefdef format to capnet (ISPD24) format" << std::endl;
        system("mkdir -p ispd24");
        globalRouter.dumpCapacities("ispd24/" + parameters.design_name + ".cap");
        globalRouter.dumpNets("ispd24/" + parameters.design_name + ".net");
        log() << "Finish transfering lefdef format to capnet (ISPD24) format" << std::endl;
        return 0;
    }

    globalRouter.route();
    globalRouter.write();
    
    logeol();
    log() << "Terminated." << std::endl;
    loghline();
    logmem();
    logeol();
}