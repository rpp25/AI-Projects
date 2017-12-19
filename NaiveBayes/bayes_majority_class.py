import re
import copy
import sys

from functools import reduce

lines = []
instances = []
groups = []
group1 = []
group2 = []
group3 = []
group4 = []
group5 = []
num_samples_train = []
num_samples_test = []
final_results = []
results_true_positive = []
results_false_positive = []
results_true_negative = []
results_false_negative = []
traingroup = []
doc_averages = [.10455, .21301, .28066, .065425, .31222, .095901, .11421, .10529, .090067, .23941,
                 .059824, .5417, .09393, .058626, .049205, .24885, .14259, .18474, 1.6621, .085577,
                 .80976, .1212, .10165, .094269, .5495, .26538, .7673, .12484, .098915, .10285,
                 .064753, .047048, .097229, .047835, .10541, .097477, .13695, .013201, .078629, .064834,
                 .043667, .13234, .046099, .079196, .30122, .17982, .0054445, .031869, .038575, .13903,
                 .016976, .26907, .075811, .044238, 5.1915, 52.173, 283.29]
# print(len(doc_averages))
feature_training_data = []

total_false_positive_rate = []
total_false_negative_rate = []
total_error_rate = []


class Instance:
    def __init__(self):
        self.word_freq_WORD = []
        self.char_freq_CHAR = []
        self.capital_run_length_average = 0
        self.capital_run_length_longest = 0
        self.capital_run_length_total = 0
        self.is_spam = False

    def toString(self):
        tempstr = ""
        count = 0

        for x in self.word_freq_WORD:
            if count < 48:
                tempstr = tempstr + str(x) + ", "
            # else:
            #     # print("\nhi")
            #     tempstr = tempstr + str(x)
            count = count + 1

        # tempstr = tempstr + "\nchar_freq_CHAR: "
        for x in self.char_freq_CHAR:
            if count < 54:
                tempstr = tempstr + str(x) + ", "
            count = count + 1

        i = 0
        if self.is_spam:
            i = 1
        tempstr = tempstr + str(self.capital_run_length_average) + ", " + str(self.capital_run_length_longest) + ", " + str(self.capital_run_length_total) + ", " + str(i)
        return tempstr

def setup(fname):
    with open(fname, 'r+') as f:
        for line in f:
            list = line.split(',')
            lines.append(list)

    f.close()
    for line in lines:
        newIn = Instance()
        count = 1
        for x in line:
            if count <= 48:
                newIn.word_freq_WORD.append(x)

            if count > 48 and count <= 54:
                newIn.char_freq_CHAR.append(x)

            if count == 55:
                newIn.capital_run_length_average = x
            if count == 56:
                newIn.capital_run_length_longest = x
            if count == 57:
                newIn.capital_run_length_total = x
            if count == 58:
                # print(lines[0][57])
                temp = int(x)
                # print(type(temp))
                if temp == 1:
                    # print("hi")
                    newIn.is_spam = True
            count = count + 1
        instances.append(newIn)


    count = 0
    group = 1
    for x in range(0, len(instances)):
        group = x % 5
        # print(group)
        if group == 0:
            # print("Line " + str(x+1) + " Group 1")
            group1.append(instances[x])
        elif group == 1:
            # print("Line " + str(x+1) + " Group 2")
            group2.append(instances[x])
        elif group == 2:
            # print("Line " + str(x+1) + " Group 3")
            group3.append(instances[x])
        elif group == 3:
            # print("Line " + str(x+1) + " Group 4")
            group4.append(instances[x])
        else:
            # print("Line " + str(x+1) + " Group 5")
            group5.append(instances[x])



def train(traingroup):
    temp_is_spam = []
    temp_not_spam = []

    temp_spam_word_less = []
    temp_spam_word_great = []
    temp_notspam_word_less = []
    temp_notspam_word_great = []

    temp_spam_char_less = []
    temp_spam_char_great = []
    temp_notspam_char_less = []
    temp_notspam_char_great = []

    temp_spam_crla_less = []
    temp_spam_crla_great = []
    temp_notspam_crla_less = []
    temp_notspam_crla_great = []

    temp_spam_crll_less = []
    temp_spam_crll_great = []
    temp_notspam_crll_less = []
    temp_notspam_crll_great = []

    temp_spam_crlt_less = []
    temp_spam_crlt_great = []
    temp_notspam_crlt_less = []
    temp_notspam_crlt_great = []

    majority_class = "non-spam"
    for inst in traingroup:
        if inst.is_spam is True:
            temp_is_spam.append(inst)
        else:
            temp_not_spam.append(inst)

    if max(len(temp_is_spam), len(temp_not_spam)) == len(temp_is_spam):
        majority_class = "spam"

    num_samples_train.append((len(temp_is_spam), len(temp_not_spam)))

    prob_spam = float(len(temp_is_spam)/(len(temp_is_spam)+len(temp_not_spam)))
    prob_nonspam = float(len(temp_not_spam)/(len(temp_is_spam)+len(temp_not_spam)))
    # for every word attribute
    for i in range(0,48):
        # spam
        # print(doc_averages[i])
        for inst in temp_is_spam:
            # f <= mu
            if float(inst.word_freq_WORD[i]) <= doc_averages[i]:
                temp_spam_word_less.append(inst)
            # f > mu
            else:
                temp_spam_word_great.append(inst)

        # non spam
        for inst in temp_not_spam:
            # f <= mu
            if float(inst.word_freq_WORD[i]) <= doc_averages[i]:
                temp_notspam_word_less.append(inst)
            # f > mu
            else:
                temp_notspam_word_great.append(inst)

        # Pr[f <= mu | spam]
        prob_less_equal_mu_spam = float(len(temp_spam_word_less)/len(temp_is_spam))
        if prob_less_equal_mu_spam == 0:
            prob_less_equal_mu_spam = 0.0014

        # Pr[f > mu | spam]
        prob_greater_mu_spam = float(len(temp_spam_word_great)/len(temp_is_spam))
        if prob_greater_mu_spam == 0:
            prob_greater_mu_spam = 0.0014
        # Pr[f <= mu | non-spam]
        prob_less_equal_mu_notspam = float(len(temp_notspam_word_less)/len(temp_not_spam))
        if prob_less_equal_mu_notspam == 0:
            prob_less_equal_mu_notspam = 0.0014
        # Pr[f > mu | non-spam]
        prob_greater_mu_notspam = float(len(temp_notspam_word_great)/len(temp_not_spam))
        if prob_greater_mu_notspam == 0:
            prob_greater_mu_notspam = 0.0014

        feature_training_data.append((prob_less_equal_mu_spam, prob_greater_mu_spam, prob_less_equal_mu_notspam, prob_greater_mu_notspam))
        # print(str(i+1))
        # print((prob_less_equal_mu_spam, prob_greater_mu_spam, prob_less_equal_mu_notspam, prob_greater_mu_notspam))
        del temp_spam_word_less[:]
        del temp_spam_word_great[:]
        del temp_notspam_word_less[:]
        del temp_notspam_word_great[:]

    # for every char attribute
    for i in range(0,6):
        # spam
        # print(doc_averages[i])
        for inst in temp_is_spam:
            # f <= mu
            if float(inst.char_freq_CHAR[i]) <= doc_averages[i+48]:
                temp_spam_char_less.append(inst)
            # f > mu
            else:
                temp_spam_char_great.append(inst)

        # non spam
        for inst in temp_not_spam:
            # f <= mu
            if float(inst.char_freq_CHAR[i]) <= doc_averages[i+48]:
                temp_notspam_char_less.append(inst)
            # f > mu
            else:
                temp_notspam_char_great.append(inst)

        # Pr[f <= mu | spam]
        prob_less_equal_mu_spam = float(len(temp_spam_char_less)/len(temp_is_spam))
        if prob_less_equal_mu_spam == 0:
            prob_less_equal_mu_spam = 0.0014

        # Pr[f > mu | spam]
        prob_greater_mu_spam = float(len(temp_spam_char_great)/len(temp_is_spam))
        if prob_greater_mu_spam == 0:
            prob_greater_mu_spam = 0.0014
        # Pr[f <= mu | non-spam]
        prob_less_equal_mu_notspam = float(len(temp_notspam_char_less)/len(temp_not_spam))
        if prob_less_equal_mu_notspam == 0:
            prob_less_equal_mu_notspam = 0.0014
        # Pr[f > mu | non-spam]
        prob_greater_mu_notspam = float(len(temp_notspam_char_great)/len(temp_not_spam))
        if prob_greater_mu_notspam == 0:
            prob_greater_mu_notspam = 0.0014

        feature_training_data.append((prob_less_equal_mu_spam, prob_greater_mu_spam, prob_less_equal_mu_notspam, prob_greater_mu_notspam))
        del temp_spam_char_less[:]
        del temp_spam_char_great[:]
        del temp_notspam_char_less[:]
        del temp_notspam_char_great[:]

    #####################################################################
    # for capital_run_length_average
    # print(doc_averages[54])
    for inst in temp_is_spam:
        # f <= mu
        if float(inst.capital_run_length_average) <= doc_averages[54]:
            temp_spam_crla_less.append(inst)
        # f > mu
        else:
            temp_spam_crla_great.append(inst)

    # non spam
    for inst in temp_not_spam:
        # f <= mu
        if float(inst.capital_run_length_average) <= doc_averages[54]:
            temp_notspam_crla_less.append(inst)
        # f > mu
        else:
            temp_notspam_crla_great.append(inst)

    # Pr[f <= mu | spam]
    prob_less_equal_mu_spam = float(len(temp_spam_crla_less)/len(temp_is_spam))
    if prob_less_equal_mu_spam == 0:
        prob_less_equal_mu_spam = 0.0014

    # Pr[f > mu | spam]
    prob_greater_mu_spam = float(len(temp_spam_crla_great)/len(temp_is_spam))
    if prob_greater_mu_spam == 0:
        prob_greater_mu_spam = 0.0014
    # Pr[f <= mu | non-spam]
    prob_less_equal_mu_notspam = float(len(temp_notspam_crla_less)/len(temp_not_spam))
    if prob_less_equal_mu_notspam == 0:
        prob_less_equal_mu_notspam = 0.0014
    # Pr[f > mu | non-spam]
    prob_greater_mu_notspam = float(len(temp_notspam_crla_great)/len(temp_not_spam))
    if prob_greater_mu_notspam == 0:
        prob_greater_mu_notspam = 0.0014

    feature_training_data.append((prob_less_equal_mu_spam, prob_greater_mu_spam, prob_less_equal_mu_notspam, prob_greater_mu_notspam))
    #########################################################################

    # print(doc_averages[55])
    # for capital_run_length_longest
    for inst in temp_is_spam:
        # f <= mu
        if float(inst.capital_run_length_longest) <= doc_averages[55]:
            temp_spam_crll_less.append(inst)
        # f > mu
        else:
            temp_spam_crll_great.append(inst)

    # non spam
    for inst in temp_not_spam:
        # f <= mu
        if float(inst.capital_run_length_longest) <= doc_averages[55]:
            temp_notspam_crll_less.append(inst)
        # f > mu
        else:
            temp_notspam_crll_great.append(inst)

    # Pr[f <= mu | spam]
    prob_less_equal_mu_spam = float(len(temp_spam_crll_less)/len(temp_is_spam))
    if prob_less_equal_mu_spam == 0:
        prob_less_equal_mu_spam = 0.0014

    # Pr[f > mu | spam]
    prob_greater_mu_spam = float(len(temp_spam_crll_great)/len(temp_is_spam))
    if prob_greater_mu_spam == 0:
        prob_greater_mu_spam = 0.0014
    # Pr[f <= mu | non-spam]
    prob_less_equal_mu_notspam = float(len(temp_notspam_crll_less)/len(temp_not_spam))
    if prob_less_equal_mu_notspam == 0:
        prob_less_equal_mu_notspam = 0.0014
    # Pr[f > mu | non-spam]
    prob_greater_mu_notspam = float(len(temp_notspam_crll_great)/len(temp_not_spam))
    if prob_greater_mu_notspam == 0:
        prob_greater_mu_notspam = 0.0014

    feature_training_data.append((prob_less_equal_mu_spam, prob_greater_mu_spam, prob_less_equal_mu_notspam, prob_greater_mu_notspam))
    #########################################################################
    # print(doc_averages[56])
    # for capital_run_length_total
    for inst in temp_is_spam:
        # f <= mu
        if float(inst.capital_run_length_total) <= doc_averages[56]:
            temp_spam_crlt_less.append(inst)
        # f > mu
        else:
            temp_spam_crlt_great.append(inst)

    # non spam
    for inst in temp_not_spam:
        # f <= mu
        if float(inst.capital_run_length_total) <= doc_averages[56]:
            temp_notspam_crlt_less.append(inst)
        # f > mu
        else:
            temp_notspam_crlt_great.append(inst)

    # Pr[f <= mu | spam]
    prob_less_equal_mu_spam = float(len(temp_spam_crlt_less)/len(temp_is_spam))
    if prob_less_equal_mu_spam == 0:
        prob_less_equal_mu_spam = 0.0014

    # Pr[f > mu | spam]
    prob_greater_mu_spam = float(len(temp_spam_crlt_great)/len(temp_is_spam))
    if prob_greater_mu_spam == 0:
        prob_greater_mu_spam = 0.0014
    # Pr[f <= mu | non-spam]
    prob_less_equal_mu_notspam = float(len(temp_notspam_crlt_less)/len(temp_not_spam))
    if prob_less_equal_mu_notspam == 0:
        prob_less_equal_mu_notspam = 0.0014
    # Pr[f > mu | non-spam]
    prob_greater_mu_notspam = float(len(temp_notspam_crlt_great)/len(temp_not_spam))
    if prob_greater_mu_notspam == 0:
        prob_greater_mu_notspam = 0.0014

    feature_training_data.append((prob_less_equal_mu_spam, prob_greater_mu_spam, prob_less_equal_mu_notspam, prob_greater_mu_notspam))

    return prob_spam, prob_nonspam, majority_class

def test(testgroup, prob_spam, prob_nonspam, majority_class):
    is_spam = []
    not_spam = []
    for test in testgroup:
        if test.is_spam is True:
            is_spam.append(test)
        else:
            not_spam.append(test)

    num_samples_test.append((len(is_spam), len(not_spam)))

    for test in testgroup:
        temp = 0
        argmax_spam = []
        argmax_nonspam = []
        # print(test.toString())
        # if test.is_spam:
        # print("Marked spam")
        for i in range(0,57):
            if i >= 0 and i < 48:
                temp = float(test.word_freq_WORD[i])
            if i >= 48 and i < 54:
                temp = float(test.char_freq_CHAR[i-48])
            if i == 54:
                temp = float(test.capital_run_length_average)
            if i == 55:
                temp = float(test.capital_run_length_longest)
            if i == 56:
                temp = float(test.capital_run_length_total)

            if temp <= doc_averages[i]:
                # print("f <= mu (" + str(doc_averages[i]) + "): " + str(temp))
                # print("\tUse feature_training_data["+ str(i) + "][0]: " + str(feature_training_data[i][0]))
                # print("\tUse feature_training_data["+ str(i) + "][2]: " + str(feature_training_data[i][2]))
                argmax_spam.append(feature_training_data[i][0])
                argmax_nonspam.append(feature_training_data[i][2])
            else:
                # print("f > mu (" + str(doc_averages[i]) + "): " + str(temp))
                # print("\tUse feature_training_data["+ str(i) + "][1]: " + str(feature_training_data[i][1]))
                # print("\tUse feature_training_data["+ str(i) + "][3]: " + str(feature_training_data[i][3]))
                argmax_spam.append(feature_training_data[i][1])
                argmax_nonspam.append(feature_training_data[i][3])

        aspam = reduce(lambda x, y: x*y, argmax_spam) * prob_spam
        anonspam = reduce(lambda x, y: x*y, argmax_nonspam) * prob_nonspam
        argmax = max(aspam, anonspam)
        # print(aspam)
        # print(anonspam)
        # print(argmax)

        if majority_class == "non-spam":
            if not test.is_spam:
                # print("Correctly classified as non-spam")
                results_true_negative.append(test)
            else:
                # print("Misclassified as non-spam")
                results_false_negative.append(test)
        else:
            if test.is_spam:
                # print("Correctly classified as spam")
                results_true_positive.append(test)
            else:
                # print("Misclassified as spam")
                results_false_positive.append(test)



if __name__ == '__main__':
    if len(sys.argv) == 2:
        fname = sys.argv[1]

    setup(fname)
    # for x in group1:
    #     print(x.is_spam)




    for i in range(0,5):
        groups.append(group5)
        groups.append(group4)
        groups.append(group3)
        groups.append(group2)
        groups.append(group1)


        testgroup = groups.pop(i)

        traingroup = []
        for group in groups:
            for inst in group:
                traingroup.append(inst)

        train_output = str(5-i) + "_Train.txt"
        f = open(train_output, "w")
        for inst in traingroup:
            # print(group.toString())
            f.write(inst.toString() + "\n")
        f.close()

        test_output = str(5-i) + "_Dev.txt"
        f = open(test_output, "w")
        for inst in testgroup:
            # print(group.toString())
            f.write(inst.toString() + "\n")
        f.close()

        pspam, pnonspam, majority = train(traingroup)
        # for x in feature_training_data:
        test(testgroup,pspam,pnonspam,majority)
        # print("True Positives: " + str(len(results_true_positive)))
        fp = 0
        fn = 0
        if len(results_false_positive) != 0 and len(results_true_positive) != 0:
            fp = len(results_false_positive)/(len(results_true_positive)+len(results_false_positive))

        # fp = len(results_false_positive)
        # print("False Positive Rate: " + str(fp))
        # print("argmax_spam length: " +str(len(argmax_spam)))
        #to do: convert to error rates

        # print("True Negatives: " + str(len(results_true_negative)))
        if len(results_false_negative) != 0 and len(results_true_negative) != 0:
            fn = len(results_false_negative)/(len(results_true_negative)+len(results_false_negative))

        # fn = len(results_false_negative)
        # print("False Negative Rate: " + str(fn))
        # print("argmax_nonspam length: " +str(len(argmax_nonspam)))
        error_rate = (len(results_false_positive) + len(results_false_negative))/len(testgroup)
        final_results.append((fp, fn, error_rate))


        total_false_positive_rate.append(fp)
        total_false_negative_rate.append(fn)
        total_error_rate.append(error_rate)

        # feature_output = str(5-i) + "_features.txt"
        # f = open(feature_output, "w")
        # for entry in feature_training_data:
        #     # print(group.toString())
        #     # feat = str(entry).strip('()')
        #     # f.write(feat + "\n")
        #
        #     for e in entry:
        #         feat_num = entry.index(e)
        #         feat = str(e)
        #         f.write(feat + "\n")
        # f.close()

        del results_true_positive[:]
        del results_false_positive[:]
        del results_true_negative[:]
        del results_false_negative[:]
        del feature_training_data[:]
        del groups[:]

    avg_fp_rate = reduce(lambda x, y: x+y, total_false_positive_rate) / len(total_false_positive_rate)
    avg_fn_rate = reduce(lambda x, y: x+y, total_false_negative_rate) / len(total_false_negative_rate)
    avg_error_rate = reduce(lambda x, y: x+y, total_error_rate) / len(total_error_rate)

    print("Iteration | # training positive examples | # training negative examples | # dev positive examples | # dev negative examples")
    for i in range(0,5):
        print("--------------------------------------------------------------------------------------------------------------------------")
        print(str(i+1) + "         | " + str(num_samples_train[i][0]) + "                         | " + str(num_samples_train[i][1]) + "                        | "
         + str(num_samples_test[i][0]) + "                     | " + str(num_samples_test[i][1]))

    for i in range(0,5):
        print("Fold " + str(i+1) + ": False Positive Rate: " + str(round(final_results[i][0], 4)) + ", False Negative Rate: " + str(round(final_results[i][1], 4)) + ", Overall Error Rate: " + str(round(final_results[i][2], 4)))
    print("")
    print("Average False Positive Rate: " + str(round(avg_fp_rate, 4)))
    print("Average False Negative Rate: " + str(round(avg_fn_rate, 4)))
    print("Average Error Rate: " + str(round(avg_error_rate, 4)))
    print("Accuracy: " + str(round(1-avg_error_rate, 4)))
