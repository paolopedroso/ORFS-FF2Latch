// This file duplicates each DFF, and also adds extra flip-flops to make sure that each enable and
// reset are clocked by the correct clock (i.e., clock 1 goes to clock 2, clock 2 goes to clock 1).

module \$_DFF_P_ (input D, C, output Q);
    wire connector;
    
    \$_DFF_P_ _TECHMAP_REPLACE_.custom_FF_replace_1 
    (.D(D), .C(C), .Q(connector));
    
    \$_DFF_P_ _TECHMAP_REPLACE_.custom_FF_replace_2 
    (.D(connector), .C(C), .Q(Q));
endmodule

module \$_DFFE_PP_ (input D, C, E, output Q);
    wire connector;
    wire enable_output;
    wire gated_clk;
    
    \$_DFF_P_ _TECHMAP_REPLACE_.custom_FF_replace_1 
    (.D(D), .C(C), .Q(connector));
    
    \$_DFF_P_ enable_FF 
    (.D(E), .C(C), .Q(enable_output));
    
    sky130_fd_sc_hd__and2_1 AND_gate_clk.gated_en 
    (.A(enable_output), .B(C), .X(gated_clk));

    \$_DFF_P_ _TECHMAP_REPLACE_.custom_gated_FF_2
    (.D(connector), .C(gated_clk), .Q(Q));
endmodule

module \$_DFFE_PN_ (input D, C, E, output Q);
    wire connector;
    wire enable_output;
    wire gated_clk;
    wire inv_en_output;
    
    \$_NOT_ INV_en
    (.A(E), .Y(inv_en_output));

    \$_DFF_P_ _TECHMAP_REPLACE_.custom_FF_replace_1 
    (.D(D), .C(C), .Q(connector));
    
    \$_DFF_P_ enable_FF 
    (.D(inv_en_output), .C(C), .Q(enable_output));
    
    sky130_fd_sc_hd__and2_1 AND_gate_clk.gated_en 
    (.A(enable_output), .B(C), .X(gated_clk));

    \$_DFF_P_ _TECHMAP_REPLACE_.custom_gated_FF_2
    (.D(connector), .C(gated_clk), .Q(Q));
endmodule


module $_SDFFE_PP0P_ (input D, C, R, E, output Q);
    wire connector;
    wire reset_output;
    wire enable_output;
    wire or_output;
    wire gated_clk;
    wire mux_output;
    
    \$_DFF_P_ _TECHMAP_REPLACE_.custom_FF_replace_1 
    (.D(D), .C(C), .Q(connector));
    
    \$_DFF_P_ reset_FF 
    (.D(R), .C(C), .Q(reset_output));
    
    \$_DFF_P_ enable_FF 
    (.D(E), .C(C), .Q(enable_output));
    
    sky130_fd_sc_hd__or2_1 OR_gate_clk 
    (.A(enable_output), .B(reset_output), .X(or_output));
    
    sky130_fd_sc_hd__and2_1 AND_gate_clk.gated_en
    (.A(or_output), .B(C), .X(gated_clk));
    
    \$_MUX_ mux_rst_inst 
    (.Y(mux_output), .A(connector), .B(1'b0), .S(reset_output));
    
    \$_DFF_P_ _TECHMAP_REPLACE_.custom_gated_FF_2
    (.D(mux_output), .C(gated_clk), .Q(Q));
endmodule

module \$_SDFFE_PN0P_ (input D, C, R, E, output Q);
    wire connector;
    wire reset_output;
    wire enable_output;
    wire inv_reset_output;
    wire or_output;
    wire gated_clk;
    wire mux_output;
    
    \$_DFF_P_ _TECHMAP_REPLACE_.custom_FF_replace_1 
    (.D(D), .C(C), .Q(connector));
    
    \$_DFF_P_ reset_FF 
    (.D(R), .C(C), .Q(reset_output));
    
    \$_DFF_P_ enable_FF 
    (.D(E), .C(C), .Q(enable_output));
    
    \$_NOT_ INV_rst 
    (.A(reset_output), .Y(inv_reset_output));
    
    sky130_fd_sc_hd__or2_1 OR_gate_clk 
    (.A(inv_reset_output), .B(enable_output), .X(or_output));
    
    sky130_fd_sc_hd__and2_1 AND_gate_clk.gated_en
    (.A(or_output), .B(C), .X(gated_clk));
    
    \$_MUX_ mux_rst_inst 
    (.Y(mux_output), .A(1'b0), .B(connector), .S(reset_output));
    
    \$_DFF_P_ _TECHMAP_REPLACE_.custom_gated_FF_2 
    (.D(mux_output), .C(gated_clk), .Q(Q));
endmodule

module \$_DFFE_PP0P_ (input D, C, R, E, output Q);
    wire connector;
    wire reset_output;
    wire enable_output;
    wire gated_clk;
    
    \$_DFF_PP0_ _TECHMAP_REPLACE_.custom_FF_replace_1 
    (.D(D), .C(C), .R(R), .Q(connector));
    
    \$_DFF_P_ reset_FF 
    (.D(R), .C(C), .Q(reset_output));
    
    \$_DFF_P_ enable_FF 
    (.D(E), .C(C), .Q(enable_output));
    
    sky130_fd_sc_hd__and2_1 AND_gate_clk.gated_en
    (.A(enable_output), .B(C), .X(gated_clk));
    
    \$_DFF_PP0_ _TECHMAP_REPLACE_.custom_gated_FF_2 
    (.D(connector), .C(gated_clk), .R(reset_output), .Q(Q));
endmodule

module \$_SDFF_PP0_ (input D, C, R, output Q);
    wire connector;
    wire reset_output;
    wire gated_clk;
    wire mux_output;
    
    \$_DFF_P_ _TECHMAP_REPLACE_.custom_FF_replace_1 
    (.D(D), .C(C), .Q(connector));
    
    \$_DFF_P_ reset_FF 
    (.D(R), .C(C), .Q(reset_output));
    
    sky130_fd_sc_hd__and2_1 AND_gate_clk.gated_en
    (.A(reset_output), .B(C), .X(gated_clk));
    
    \$_MUX_ mux_rst_inst 
    (.Y(mux_output), .A(1'b0), .B(connector), .S(reset_output));
    
    \$_DFF_P_ _TECHMAP_REPLACE_.custom_gated_FF_2 
    (.D(mux_output), .C(gated_clk), .Q(Q));
endmodule

module \$_SDFF_PP1_ (input D, C, R, output Q);
    wire connector;
    wire reset_output;
    wire mux_output;
    
    \$_DFF_P_ _TECHMAP_REPLACE_.custom_FF_replace_1 
    (.D(D), .C(C), .Q(connector));
    
    \$_DFF_P_ reset_FF
    (.D(R), .C(C), .Q(reset_output));
    
    \$_MUX_ mux_set_inst 
    (.Y(mux_output), .A(connector), .B(1'b1), .S(reset_output));
    
    \$_DFF_P_ _TECHMAP_REPLACE_.custom_FF_replace_2 
    (.D(mux_output), .C(C), .Q(Q));
endmodule

module \$_DFF_PP0_ (input D, C, R, output Q);
    wire connector;
    wire reset_FF_output;
    
    \$_DFF_PP0_ _TECHMAP_REPLACE_.custom_FF_replace_1 (.D(D), .C(C), .R(R), .Q(connector));

    \$_DFF_P_ reset_FF  (.D(R), .C(C), .Q(reset_FF_output));

    \$_DFF_PP0_ _TECHMAP_REPLACE_.custom_FF_replace_2 (.D(connector), .C(C), .R(reset_FF_output), .Q(Q));
endmodule

module \$_DFF_PN0_ (input D, C, R, output Q);
    wire connector;
    wire inv_reset_output;

    \$_NOT_ INV_rst
    (.A(R), .Y(inv_reset_output));

    \$_DFF_PP0_ _TECHMAP_REPLACE_.custom_FF_replace_1 (.D(D), .C(C), .R(inv_reset_output), .Q(connector));

    wire reset_FF_output;
    \$_DFF_P_ reset_FF  (.D(inv_reset_output), .C(C), .Q(reset_FF_output));

    \$_DFF_PP0_ _TECHMAP_REPLACE_.custom_FF_replace_2 (.D(connector), .C(C), .R(reset_FF_output), .Q(Q));
endmodule

//////////////////////////////////////// added modules ////////////////////////////////////////

module \$_SDFF_PN1_ (input D, C, R, output Q);
    wire connector;
    wire reset_output;
    wire mux_output;
    
    \$_DFF_P_ _TECHMAP_REPLACE_.custom_FF_replace_1 
    (.D(D), .C(C), .Q(connector));
    
    \$_DFF_P_ reset_FF 
    (.D(R), .C(C), .Q(reset_output));
    
    \$_MUX_ mux_set_inst 
    (.Y(mux_output), .A(1'b1), .B(connector), .S(reset_output));
    
    \$_DFF_P_ _TECHMAP_REPLACE_.custom_FF_replace_2 
    (.D(mux_output), .C(C), .Q(Q));
endmodule

module \$_SDFF_PN0_ (input D, C, R, output Q);
    wire connector;
    wire reset_output;
    wire mux_output;
    
    \$_DFF_P_ _TECHMAP_REPLACE_.custom_FF_replace_1 
    (.D(D), .C(C), .Q(connector));
    
    \$_DFF_P_ reset_FF 
    (.D(R), .C(C), .Q(reset_output));
    
    \$_MUX_ mux_rst_inst 
    (.Y(mux_output), .A(1'b0), .B(connector), .S(reset_output));
    
    \$_DFF_P_ _TECHMAP_REPLACE_.custom_FF_replace_2 
    (.D(mux_output), .C(C), .Q(Q));

endmodule

module \$_DFF_PN1_ (input D, C, R, output Q);
    wire connector;
    wire reset_output;
    wire mux_output;
    wire inv_reset_output;
    wire or_output;
    
    \$_DFF_P_ _TECHMAP_REPLACE_.custom_FF_replace_1 
    (.D(D), .C(C), .Q(connector));

    \$_DFF_P_ reset_FF 
    (.D(R), .C(C), .Q(reset_output));

    \$_MUX_ mux_set_inst 
    (.Y(mux_output), .A(1'b1), .B(connector), .S(reset_output));

    \$_NOT_ INV_rst 
    (.A(R), .Y(inv_reset_output));
    
    sky130_fd_sc_hd__or2_1 OR_gate_clk.gated_en
    (.A(inv_reset_output), .B(C), .X(or_output));
        
    \$_DFF_P_ _TECHMAP_REPLACE_.custom_gated_FF_2 
    (.D(mux_output), .C(or_output), .Q(Q));
endmodule

module \$_DFF_NN0_ (input D, C, R, output Q);
    wire connector;
    wire reset_output;

    \$_DFF_P_ reset_FF
    (.D(R), .C(C), .Q(reset_output));
    
    \$_DFF_PP0_ _TECHMAP_REPLACE_.custom_FF_replace_2
    (.D(D), .C(C), .R(R), .Q(connector));
    
    \$_DFF_PP0_ _TECHMAP_REPLACE_.custom_FF_replace_1
    (.D(connector), .C(C), .R(reset_output), .Q(Q));
endmodule

module \$_DLATCH_N_ (input E, D, output Q);

    wire connector;
    
    \$_DFF_P_ _TECHMAP_REPLACE_.custom_FF_replace_2 
    (.D(D), .C(E), .Q(connector));
    
    \$_DFF_P_ _TECHMAP_REPLACE_.custom_FF_replace_1
    (.D(connector), .C(E), .Q(Q));

endmodule
