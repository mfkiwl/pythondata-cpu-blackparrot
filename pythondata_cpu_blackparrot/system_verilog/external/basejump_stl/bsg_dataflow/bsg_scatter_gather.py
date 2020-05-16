#!/usr/bin/python

import sys;
import math;

# Given a bit vector, generate
# permutation vectors that perform
# concentration (fwd) and deconcentration (bkwd).
#
#
#           bit   fwd          bkwd
#   pos.   vec    vec          vec
#     3     1 --\    1      --- 2
#                \         /
#     2     1 -\  -> 3  <--  -- 1
#               \           /
#     1     0    --> 2  <---    3 --> 1

#     0     1 -----> 0  <------ 0
#
#


max_channel = 12;

# input
channels = [x for x in range(1,max_channel)];

# converts from an integer to a list of bit integers
def int_to_bit_list(a,pad) :
    b = [int(x) for x in bin(a)[2:]]
    return ([0] * (pad - len(b))) + b;

def print_bit_list(a) :
    for x in a :
        sys.stdout.write(str(x))

def bits_to_rep(x) :
    return len(bin(x-1))-2;

def print_case_line(a,result,var_name,result_x):
    print "        ",str(len(a))+"'b",
    print_bit_list(a)
    print ": "+var_name+" = ",str(bits_to_rep(len(a))*len(a))+"'b",
    for x in reversed(result) :
        print_bit_list(int_to_bit_list(x,bits_to_rep(len(a))));
        #sys.stdout.write("_")
    print "; // ", ' '.join([str(y) for y in reversed(result_x)]);

def gen_vec(channels, fn) :

    print("    always_comb");
    print("    unique case (vec_i) ");

    for j in range(0,2**channels) :
        q = fn(int_to_bit_list(j,channels))

    print ("        default: "+q+"= 'X;");
    print ("    endcase");

def gen_fwd_vec_line_helper(a,dpath) :
    i = 0;
    spare = -1;
    pos  = 0;
    result = [];
    result_x = [];

    for x in reversed(a) :
        if (x) :
            if (dpath) :
                result.append(i-pos);
            else :
                result.append(i);
            pos = pos+1;
        else :
            spare = i;
        i = i+1;

    # add unused items
    result_x = result + [ "X" ] * (len(a)-len(result));

    if (dpath) :
        result = result +  [0] * (len(a)-len(result));
        print_case_line (a,result,"fwd_datapath_o",result_x);
        return "fwd_datapath_o"
    else: 
        result = result + [spare] * (len(a)-len(result));
        print_case_line (a,result,"fwd_o",result_x);
        return "fwd_o"
    # print it all out
    

def gen_fwd_vec_line_dpath(a) :
    return gen_fwd_vec_line_helper(a,1);

def gen_fwd_vec_line(a) :
    return gen_fwd_vec_line_helper(a,0);

def gen_back_vec_line_helper(a,dpth) :
    i = 0;
    result = [];
    result_x = [];

    # number all of the bits that are set
    # for forward permutation
    for x in reversed(a) :
        if (x) :
            result.append(i);
            result_x.append(i);
            i = i+1;
        else :
            # this is always a safe value
            # any other unused value would be okay
            # too, and possibly will reduce logic.
            if (dpth) :
                result.append(0),
            else :
                result.append(len(a)-1),
            result_x.append("X");

    if (dpth) :
        print_case_line (a,result,"bk_datapath_o",result_x);
        return "bk_datapath_o";
    else :
        print_case_line (a,result,"bk_o",result_x);
        return "bk_o";

def gen_back_vec_line_dpath(a) :
    return gen_back_vec_line_helper(a,1);

def gen_back_vec_line(a) :
    return gen_back_vec_line_helper(a,0);


def generate_code_for_channel(chan) :

    print "\nif (vec_size_lp == "+str(chan)+")"
    print "  begin"

    print "    // backward vec";

    gen_vec(chan,gen_back_vec_line)

    print "\n    // backward vec datapath";

    gen_vec(chan,gen_back_vec_line_dpath)

    
    print "\n    // fwd vec";

    gen_vec(chan,gen_fwd_vec_line)

    print "\n    // fwd datapath vec";

    gen_vec(chan,gen_fwd_vec_line_dpath)



    print ("  end")




print """
// MBT 8-18-2014
// bsg_scatter_gather
// generated by bsg_scatter_gather.py;
// python-generated Code. do not modify
//
//
// Given a bit vector, generate
// permutation vectors that perform
// concentration (fwd) and deconcentration (bkwd).
//
//
//           bit   fwd          bkwd
//   pos.   vec    vec          vec
//     3     1 --\    1      --- 2
//                \         /
//     2     1 -\  -> 3  <--  -- 1
//               \           /
//     1     0    --> 2  <---    3 --> 1

//     0     1 -----> 0  <------ 0
//
// For empty slots; we just pick an unused slot, possible
// reusing the same empty slot multiple times. This allows
// control logic to be unselected.
//


module bsg_scatter_gather #(parameter vec_size_lp="inv")
       (input [vec_size_lp-1:0] vec_i
       ,output reg [vec_size_lp*`BSG_SAFE_CLOG2(vec_size_lp)-1:0] fwd_o
       ,output reg [vec_size_lp*`BSG_SAFE_CLOG2(vec_size_lp)-1:0] fwd_datapath_o
       ,output reg [vec_size_lp*`BSG_SAFE_CLOG2(vec_size_lp)-1:0] bk_o
       ,output reg [vec_size_lp*`BSG_SAFE_CLOG2(vec_size_lp)-1:0] bk_datapath_o       
       );
"""


for x in channels :
    generate_code_for_channel(x)

print "// synopsys translate_off";
print "initial assert (vec_size_lp < ",max_channel,") else $error(\"bsg_scatter_gather: vec_size_lp too large %d\", vec_size_lp);";
print "// synopsys translate_on";

print "endmodule";

#for i in range(1,10) :
#    print i,bits_to_rep(i)
