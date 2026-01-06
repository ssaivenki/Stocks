from flask import Flask, request, jsonify
from pulp import LpProblem, LpVariable, lpSum, LpMinimize, PULP_CBC_CMD, LpBinary
# import database_connector  # Replace with actual module to fetch from DUT DB

app = Flask(__name__)

# Constants
CH4_LHV_MMBTU_PER_1000SCF = 1.012
CH4_LHV_MMBTU_PER_SCF = CH4_LHV_MMBTU_PER_1000SCF / 1000

DAIRY_DB = {
    f"dairy_{i+1}": {
        "current_flow_rate_scfm": 100 + i * 10,
        "CH4_pct": 0.98,              # Higher CH4 for successful optimization
        "CO2_pct": 0.03,
        "O2_pct": 0.005,             # Still safe
        "N2_pct": 0.02,               # Still safe
        "H2S_ppm": 100,                  # Still safe
        "time_delay_sec": 30,
        "max_flow_rate_scfm":150+i*2
    }
    for i in range(11)
}

@app.route('/optimize_flow_rates', methods=['GET'])
def optimize_flow_rates():
    try:
        # import pdb;pdb.set_trace()  # Debugging breakpoint
        # Step 1: Input Validation
        # data = request.get_json()
        # desired_energy = data.get('desired_energy_mmbtu_per_h', None)
        desired_energy = 80
        if not desired_energy or desired_energy <= 0:
            return jsonify({"status": "failure", "error": "Invalid energy target. Please enter a positive number."}), 400

        # # Step 2: Fetch Real-Time Data
        # try:
        #     dairies = database_connector.fetch_dairy_data()  # Returns list of dicts for each dairy
        # except Exception:
        #     return jsonify({"status": "failure", "error": "Database connection failed."}), 500

        # For demonstration, we use a static dictionary
        dairies = DAIRY_DB
        if not dairies:
            return jsonify({"status": "failure", "error": "No dairy data available."}), 500
        required_ch4_scfm = desired_energy / (CH4_LHV_MMBTU_PER_SCF * 60)
        active_dairies = {}

        # Step 3: Apply Safety Cutoffs
        for dairy_id, params in dairies.items():
            if (params['O2_pct'] > 1 or params['N2_pct'] > 5 or params['H2S_ppm'] > 300):
                continue
            active_dairies[dairy_id] = params

        if not active_dairies:
            return jsonify({"status": "failure", "error": "All dairies failed safety cutoffs."}), 400



        # Step 4: Optimization Setup
        prob = LpProblem("OptimizeGasFlow", LpMinimize)
        flow_vars = {d: LpVariable(f"flow_{d}", 100, dairies[d]['max_flow_rate_scfm']) for d in active_dairies}

        total_flow = lpSum(flow_vars[d] for d in active_dairies)
        total_ch4_flow = lpSum(flow_vars[d] * (dairies[d]['CH4_pct']) for d in active_dairies)


        # ‑‑ decision variables ‑‑
        for d in active_dairies:
            print(d)

        # new binary: 1 = site used, 0 = site off
        use_site = {
            d: LpVariable(f"use_{d}", cat=LpBinary)
            for d in active_dairies
        }

        BIG_M = max(active_dairies[d]['max_flow_rate_scfm'] for d in active_dairies)

        for d in active_dairies:
            # if use_site[d] == 0  ⇒  flow_d must be 0
            prob += flow_vars[d] <= BIG_M * use_site[d], f"ShutOffLink_{d}"

        PENALTY = 10000  # “cost units” for every site turned off

        total_flow = lpSum(flow_vars[d] for d in active_dairies)
        shutdown_cost = lpSum((1 - use_site[d]) * PENALTY for d in active_dairies)

        # new objective: minimise (real flow + penalty for unused sites)
        prob += total_flow + shutdown_cost


        #prob += total_flow  # Optional: minimize total flow
        prob += total_ch4_flow >= required_ch4_scfm, "EnergyConstraint"
        prob += total_ch4_flow >= 0.97 * total_flow, "PurityConstraint"
        print(prob)
        prob.solve(PULP_CBC_CMD(msg=False))
        status = prob.solve(PULP_CBC_CMD(msg=True))


        # Step 5: Output
        if prob.status != 1:
            suggested_energy = desired_energy * 0.9
            return jsonify({
                "status": "failure",
                "error": "Desired energy and purity targets cannot be met with current gas compositions.",
                "suggested_energy_target": round(suggested_energy, 2)
            }), 200

        suggested_rates = {
            dairy_id: round(flow_vars[dairy_id].varValue, 2)
            for dairy_id in active_dairies
        }

        achieved_energy = sum(
            flow_vars[d].varValue * (dairies[d]['CH4_pct'] / 100) * CH4_LHV_MMBTU_PER_SCF * 60
            for d in active_dairies
        )

        ch4_pct_at_hub = sum(
            flow_vars[d].varValue * (dairies[d]['CH4_pct'] / 100)
            for d in active_dairies
        ) / sum(flow_vars[d].varValue for d in active_dairies)

        return jsonify({
            "status": "success",
            "suggested_flow_rates": suggested_rates,
            "achieved_energy_mmbtu_per_h": round(achieved_energy, 2),
            "ch4_pct_at_hub": round(ch4_pct_at_hub * 100, 2)
        }), 200

    except Exception as e:
        return jsonify({"status": "failure", "error": f"Unhandled exception: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)