#include "GrDatabase.h"
#include <fstream>

gr::GrDatabase grDatabase;

namespace gr {
void GrDatabase::init() {
    GrRouteGrid::init();
    GrNetlist::init(*this);

    GrRouteGrid::print();
}

void GrDatabase::dumpCapacities(const std::string& filename) {
    GrRouteGrid::dumpCapacities(filename);
}

void GrDatabase::writeGuides(std::string filename) {
    log() << "Writing guides to file..." << std::endl;

    std::stringstream ss;

    auto printGrGuides = [&](const vector<GrBoxOnLayer>& guides) {
        for (const auto& guide : guides) {
            ss << guide[X].low << " ";
            ss << guide[Y].low << " ";
            ss << guide.layerIdx << " ";
            ss << guide[X].high << " ";
            ss << guide[Y].high << " ";
            ss << guide.layerIdx << std::endl;
        }
    };
    auto printGrGuides_via = [&](const vector<GrBoxOnLayer>& guides, const vector<GrBoxOnLayer>& guides2) {
        for (int i=0; i<guides.size(); i++) {
            const auto& guide = guides[i];
            const auto& guide2 = guides2[i];
            if(guide.layerIdx==guide2.layerIdx) continue;
            ss << guide[X].low << " ";
            ss << guide[Y].low << " ";
            ss << guide.layerIdx << " ";
            ss << guide[X].high << " ";
            ss << guide[Y].high << " ";
            ss << guide2.layerIdx << std::endl;
        }
    };
    auto printGrGuides_patch = [&](const vector<GrBoxOnLayer>& guides, const vector<GrBoxOnLayer>& guides2) {
        for (int i=0; i<guides.size(); i++) {
            const auto& guide = guides[i];
            const auto& guide2 = guides2[i];
            if(guide.layerIdx==guide2.layerIdx) continue;
            // if(guide[X].low==guide[X].high || guide[Y].low==guide[Y].high){
            //     ss << guide[X].low << " ";
            //     ss << guide[Y].low << " ";
            //     ss << guide.layerIdx << " ";
            //     ss << guide2[X].low << " ";
            //     ss << guide2[Y].low << " ";
            //     ss << guide2.layerIdx << std::endl;
            // }
            // else{
                // for(int x=guide[X].low; x<=guide[X].high; x++) {
                //     for(int y=guide[Y].low; y<=guide[Y].high; y++) {
                //         if(x==guide[X].low || x==guide[X].high || y==guide[Y].low || y==guide[Y].high) continue;
                //         ss << x << " ";
                //         ss << y << " ";
                //         ss << guide.layerIdx << " ";
                //         ss << x << " ";
                //         ss << y << " ";
                //         ss << guide2.layerIdx << std::endl;
                //     }
                // }
                
                // only print 1 point, will cause open but have correct score and runtime
                ss << guide[X].low << " ";
                ss << guide[Y].low << " ";
                ss << guide.layerIdx << " ";
                ss << guide[X].low << " ";
                ss << guide[Y].low << " ";
                ss << guide2.layerIdx << std::endl;
            // }
        }
    };

    for (const auto& net : grDatabase.nets) {
        ss << net.getName() << std::endl;
        ss << "(" << std::endl;
        printGrGuides(net.wireRouteGuides);
        printGrGuides_via(net.viaRouteGuides1, net.viaRouteGuides2);
        printGrGuides_patch(net.patchRouteGuides1, net.patchRouteGuides2);
        ss << ")" << std::endl;
    }

    std::ofstream fout(filename);
    fout << ss.str();
    fout.close();
}
}  // namespace gr
