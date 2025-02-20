def conc_res(qc) :
    res = []

    result1 = AerSimulator().run(qc).result()
    count1s = result1.get_counts()
    res.append(count1s)
    print(counts1)

    result2 = TerraSampler().run(qc).result()
    counts2 = pub_result2.quasi_dists[0]
    res.append(count2s)
    print(counts2)

    return res

def print_res_by_sim(nom_sim) :
    res = conc_res(qc)

    match nom_sim:
        case "AER":
            plot_histogram(res[1])
        case "STV":
            plot_histogram(res[2])
        case "UNIT":
            plot_histogram(res[3])
        case "DENS":
            plot_histogram(res[4])
        case "STAB":
            plot_histogram(res[5])
        case "MAPROD":
            plot_histogram(res[6])
        case _:
            print("Bad simulator request !")
    
    plt.show()

##################################################################################################################################################
#
# Many simulators : AerSimulator, StatevectorSimulator, UnitarySimulator, DensityMatrixSimulator, StabilizerSimulator, MatrixProductStateSimulator
# 
##################################################################################################################################################